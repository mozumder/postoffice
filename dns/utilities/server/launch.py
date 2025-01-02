import asyncio
import logging
import uuid

from django.conf import settings
from aiomultiprocess import Pool

from .protocol import worker_launcher, DNSProtocol, handle_dns_query

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

    control_queue = asyncio.Queue()
    status_queue = asyncio.Queue()
    tcp_send_queue = asyncio.Queue()
    tcp_receive_queue = asyncio.Queue()
    udp_send_queue = asyncio.Queue()
    udp_receive_queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    processes = options['processes']
    async with Pool() as multiproc_pool:
        while True:
            tasks = []

            for i in range(processes):
                id = uuid.uuid4()
                opts = [id, control_queue, status_queue, udp_receive_queue, udp_send_queue, tcp_receive_queue, tcp_send_queue, dsn, loglevel]
                tasks.append(multiproc_pool.apply(worker_launcher, [opts])) 
#                tasks.append(multiproc_pool.apply(put_message, [udp_receive_queue,'Test']))
            logger.debug(f'tasks = {len(tasks)}')
            all_workers = asyncio.gather(*tasks)
            logger.debug(all_workers)
#            await udp_receive_queue.put(b'P\x94\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x07example\x03net\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x00')
            # Create TCP server
            tcp_server = await asyncio.start_server(
                lambda reader, writer: handle_dns_query(reader, writer, tcp_send_queue, tcp_receive_queue), ip_address, port)

            # Create UDP server
            udp_transport, _ = await loop.create_datagram_endpoint(
                lambda: DNSProtocol(udp_send_queue, udp_receive_queue, control_queue), local_addr=(ip_address, port))

            logger.debug(f"TCP server listening on {ip_address}:{port}")
            logger.debug(f"UDP server listening on {ip_address}:{port}")                
            await asyncio.sleep(3600)
            udp_transport.close()
            tcp_server.close()
            for i in range(len(tasks)):
                await control_queue.put("stop")
