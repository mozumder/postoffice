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
    async with Pool() as pool:
        while True:

            results = asyncio.gather(*[ 
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
                    ]]) for i in range(processes)])
#            await tcp_receive_queue.put(b'\x00,[?\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x03www\x07example\x03net\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x00')
#            await udp_receive_queue.put(b'C\xce\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x03www\x07example\x03net\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x00')
            # Create TCP server
            tcp_server = await asyncio.start_server(
                lambda reader, writer: handle_dns_query(reader, writer, tcp_send_queue, tcp_receive_queue), ip_address, port)

            # Create UDP server
            udp_transport, _ = await loop.create_datagram_endpoint(
                lambda: DNSProtocol(udp_send_queue, udp_receive_queue), local_addr=(ip_address, port))

            logger.debug(f"TCP server listening on {ip_address}:{port}")
            logger.debug(f"UDP server listening on {ip_address}:{port}")                

            try:
                await asyncio.sleep(4)
            finally:
                udp_transport.close()
                tcp_server.close()
                for i in range(processes):
                    await control_queue.put("stop")
