import asyncio
from django.conf import settings
import asyncpg

from .protocol import DNSServerProtocol

def LaunchDNSServer(ip_address='127.0.0.1', port=53, processes=1):
    while True:
        asyncio.run(UDPListener(ip_address, port, processes),)

async def UDPListener(ip_address='127.0.0.1', port=53, processes=1):
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
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: DNSServerProtocol(dsn,processes),
        local_addr=(ip_address, port))

    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()
