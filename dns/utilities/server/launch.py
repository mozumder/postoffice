import asyncio
from django.conf import settings
import asyncpg

from .protocol import MultiprocessorDNSServer, DNSServer

def LaunchDNSServer(ip_address='127.0.0.1', port=53, processes=1, test_mode=False):
    while True:
        asyncio.run(UDPListener(ip_address, port, processes,test_mode),)

async def UDPListener(ip_address='127.0.0.1', port=53, processes=1, test_mode=False):
    if test_mode:
        db_name = 'test_'+settings.DATABASES['default']['NAME']
    else:
        db_name = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    dsn = f'postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    # One protocol instance will be created to serve all
    # client requests.
    if processes > 1:
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: MultiprocessorDNSServer(dsn,processes),
            local_addr=(ip_address, port))
    else:
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: DNSServer(dsn,processes),
            local_addr=(ip_address, port))

    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()
