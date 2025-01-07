import asyncio
import logging
import uuid
from multiprocessing import Manager
from multiprocessing.queues import Queue
import traceback
from queue import Empty

from django.conf import settings
from aiomultiprocess import Pool

from .protocol import worker, DNSProtocol, handle_dns_query


async def dns_main(*args, **options):
    logger = logging.getLogger("dnsserver")
    logger.info("Running DNS server")

    ip_address = options['ip_address']
    port = options['port']
    if options['debug'] == True:
        logger.info('Turning on debug messages')
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logger.setLevel(loglevel)

    if options['test_mode'] == True:
        db_name = 'test_'+settings.DATABASES['default']['NAME']
    else:
        db_name = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    dsn = f'postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

    control_queue: Queue = Manager().Queue()
    status_queue: Queue = Manager().Queue()
    send_queue: Queue = Manager().Queue()
    receive_queue: Queue = Manager().Queue()

    processes = options['processes']
    timeout = 14400
    loop = asyncio.get_running_loop()
    while True:
        async with asyncio.TaskGroup() as tg:
            query_handlers_tasks = tg.create_task(query_handlers_launcher(processes, dsn, control_queue, status_queue, send_queue, receive_queue, loglevel))
            server_tasks = tg.create_task(server_launcher(ip_address, port, dsn, loop, control_queue, status_queue, send_queue, receive_queue))
            watchdog_task = tg.create_task(watchdog_timer(processes, query_handlers_tasks, server_tasks, timeout, control_queue, status_queue, send_queue, receive_queue))

async def watchdog_timer(processes, query_handlers_tasks, server_tasks, timeout, control_queue, status_queue, send_queue, receive_queue):
    logger = logging.getLogger("dnsserver")

    await asyncio.sleep(timeout)

    logger.info(f'Stopping DNS server')
    server_tasks.cancel()
    try:
        await server_tasks
    except asyncio.CancelledError:
        logger.debug("udp_server_tasks is cancelled now")

    for i in range(processes):
        control_queue.put("stop")
        logger.debug(f"sent stop {i}")

    for i in range(processes):
        try:
            msg = status_queue.get()
            if msg == "stopped":
                # Process the item
                logger.debug(f"stop {i} acknowledged: {msg}")
                continue
        except Empty:
            logger.debug(f'empty control queue')
            raise
        except Exception:
            traceback.print_exc()
            raise

async def query_handlers_launcher(processes, dsn, control_queue, status_queue, send_queue, receive_queue, loglevel):
    logger = logging.getLogger("dnsserver")
    logger.debug(f"Launching handlers")
    try:
        async with Pool(maxtasksperchild=1, childconcurrency=1) as pool:
            logger.debug(f"Mapping tasks")
            results = await pool.map(
                    worker, [[
                        control_queue, 
                        status_queue, 
                        receive_queue, 
                        send_queue, 
                        dsn, 
                        loglevel
                    ] for _ in range(processes)])
    except asyncio.CancelledError as e:
        raise
    except Exception:
        traceback.print_exc()
        raise
    finally:
        logger.debug(f"Stopped handlers")

async def server_launcher(ip_address, port, dsn, loop, control_queue, status_queue, send_queue, receive_queue):
    logger = logging.getLogger("dnsserver")
    logger.debug(f"Launching UDP Server")
    udp_transport, _ = await loop.create_datagram_endpoint(
        lambda: DNSProtocol(send_queue, receive_queue), local_addr=(ip_address, port))
    logger.debug(f"Launching TCP Server")
    tcp_server = await asyncio.start_server(
        lambda reader, writer: handle_dns_query(reader, writer, send_queue, receive_queue), ip_address, port)
    addrs = ', '.join(str(sock.getsockname()) for sock in tcp_server.sockets)
    logger.info(f'Serving DNS on {addrs}')

    try:
        while True:
            await asyncio.sleep(3600)  # Essentiall run forever until cancelled
    except asyncio.CancelledError as e:
        logger.debug(f"Stopping Servers")
    finally:
        udp_transport.close()
        tcp_server.close()

#            await tcp_receive_queue.put(b'\x00,[?\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x03www\x07example\x03net\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x00')
#            await udp_receive_queue.put(b'C\xce\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x03www\x07example\x03net\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x00')
   
