import asyncio
import logging
import uuid
from multiprocessing import Manager
from multiprocessing.queues import Queue

from django.conf import settings
from aiomultiprocess import Pool

from .protocol import worker_launcher, DNSProtocol, handle_dns_query, udp_server

logger = logging.getLogger("dnsserver")

async def dns_main(*args, **options):
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
    tcp_send_queue: Queue = Manager().Queue()
    tcp_receive_queue: Queue = Manager().Queue()
    udp_send_queue: Queue = Manager().Queue()
    udp_receive_queue: Queue = Manager().Queue()

    processes = options['processes']
    loop = asyncio.get_running_loop()
    while True:
        async with asyncio.TaskGroup() as tg:
            query_handlers_tasks = tg.create_task(query_handlers_launcher(processes, dsn, control_queue, status_queue, tcp_send_queue, tcp_receive_queue, udp_send_queue, udp_receive_queue, loglevel))
            tcp_server_tasks = tg.create_task(tcp_server_launcher(ip_address, port, dsn, loop, control_queue, status_queue, tcp_send_queue, tcp_receive_queue, loglevel))
            udp_server_tasks = tg.create_task(udp_server_launcher(ip_address, port, dsn, loop, control_queue, status_queue, udp_send_queue, udp_receive_queue, loglevel))
            watchdog_task = tg.create_task(watchdog_timer(query_handlers_tasks, tcp_server_tasks, udp_server_tasks, 4, control_queue, status_queue, tcp_send_queue, tcp_receive_queue, udp_send_queue, udp_receive_queue))

async def watchdog_timer(query_handlers_tasks, tcp_server_tasks, udp_server_tasks, timeout, control_queue, status_queue, tcp_send_queue, tcp_receive_queue, udp_send_queue, udp_receive_queue):
    logger.debug(f"Running watchdog timer")

#    await control_queue.put("stop")
    await asyncio.sleep(timeout)
    await control_queue.put("stop")
    return
    try:
#        await asyncio.sleep(timeout)
#        await tcp_receive_queue.put(b'\x00,[?\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x03www\x07example\x03net\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x00')
#        await udp_receive_queue.put(b'C\xce\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x03www\x07example\x03net\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x00')
#        await control_queue.put("stop")
        await asyncio.sleep(timeout)
        await control_queue.put("stop")
    finally:
        query_handlers_tasks.cancel()
        try:
            await query_handlers_tasks
        except asyncio.CancelledError:
            logger.debug("query_handlers_tasks is cancelled now")

        tcp_server_tasks.cancel()
        try:
            await tcp_server_tasks
        except asyncio.CancelledError:
            logger.debug("tcp_server_tasks is cancelled now")

        udp_server_tasks.cancel()
        try:
            await udp_server_tasks
        except asyncio.CancelledError:
            logger.debug("udp_server_tasks is cancelled now")

async def query_handlers_launcher(processes, dsn, control_queue, status_queue, tcp_send_queue, tcp_receive_queue, udp_send_queue, udp_receive_queue, loglevel):
    logger.debug(f"Launching handlers")
    try:
        async with Pool(maxtasksperchild=1, childconcurrency=1) as pool:
            logger.debug(f"Mapping tasks")
            results = await pool.map(
                    worker_launcher, [[
                        uuid.uuid4(), 
                        control_queue, 
                        status_queue, 
                        udp_receive_queue, 
                        udp_send_queue, 
                        tcp_receive_queue, 
                        tcp_send_queue, 
                        dsn, 
                        loglevel,
                    ] for _ in range(processes)])
            logger.debug(f"Tasks done")
            logger.debug(results)
    except asyncio.CancelledError as e:
        logger.debug(f"Stopping handlers")
        for i in range(processes):
            control_queue.put("stop")
            logger.debug(f"Sent stop msg")
        for i in range(processes):
            logger.debug(f"Awaiting acknowledgement")
            msg = status_queue.get()
            logger.debug(msg)
        raise
    finally:
        logger.debug(f"Stopped handlers")

        
async def tcp_server_launcher(ip_address, port, dsn, loop, control_queue, status_queue, tcp_send_queue, tcp_receive_queue, loglevel):
    logger.debug(f"Launching TCP Server")
    await asyncio.sleep(3600)
    return
    pass

async def udp_server_launcher(ip_address, port, dsn, loop, control_queue, status_queue, udp_send_queue, udp_receive_queue, loglevel):
    logger.debug(f"Launching UDP Server")
    await asyncio.sleep(3600)
    return
    try:
        udp_transport, _ = await loop.create_datagram_endpoint(
            lambda: DNSProtocol(udp_send_queue, udp_receive_queue), local_addr=(ip_address, port))
    except asyncio.CancelledError as e:
        logger.debug(f"Stopping UDP Server")
        udp_transport.close()
        raise

    #                udp_transport.close()
    #                tcp_server.close()
    #    for i in range(processes):
    #        await control_queue.put("stop")

"""
    async with Pool() as pool:
        while True:

            handler_tasks = [ 
                pool.apply(
                    worker_launcher,
                    [[
                        uuid.uuid4(), 
                        control_queue, 
                        status_queue, 
                        udp_receive_queue, 
                        udp_send_queue, 
                        tcp_receive_queue, 
                        tcp_send_queue, 
                        dsn, 
                        loglevel
                    ]]) for i in range(processes)]
#            await tcp_receive_queue.put(b'\x00,[?\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x03www\x07example\x03net\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x00')
#            await udp_receive_queue.put(b'C\xce\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x03www\x07example\x03net\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x00')
            # Create TCP server
#            tcp_server = await asyncio.start_server(
#                lambda reader, writer: handle_dns_query(reader, writer, tcp_send_queue, tcp_receive_queue), ip_address, port)

            # Create UDP server
#            udp_transport, _ = await loop.create_datagram_endpoint(
#                lambda: DNSProtocol(udp_send_queue, udp_receive_queue), local_addr=(ip_address, port))

#            serve = await asyncio.create_task(udp_server(udp_receive_queue, udp_send_queue, ip_address, port))
#            tasks.append(loop.call_soon(functools.partial(asyncio.start_server,
#               lambda reader, writer: handle_dns_query(reader, writer, tcp_send_queue, tcp_receive_queue), ip_address, port)))
#            tasks.append(loop.call_soon(functools.partial(loop.create_datagram_endpoint, 
#                lambda: DNSProtocol(udp_send_queue, udp_receive_queue), local_addr=(ip_address, port))))

#            tasks.append(asyncio.start_server(lambda reader, writer: handle_dns_query(reader, writer, tcp_send_queue, tcp_receive_queue), ip_address, port))
#            tasks.append(loop.create_datagram_endpoint(lambda: DNSProtocol(udp_send_queue, udp_receive_queue), local_addr=(ip_address, port))) 

            results = asyncio.gather(*tasks)

            logger.debug(f"TCP server listening on {ip_address}:{port}")
            logger.debug(f"UDP server listening on {ip_address}:{port}")                


            udp_server_task = asyncio.create_task(launch_udp_server())
            tcp_server_task = asyncio.create_task(launch_tcp_server())
            timer_task = await asyncio.create_task(udp_server_task, tcp_server_task, handler_tasks)
"""
