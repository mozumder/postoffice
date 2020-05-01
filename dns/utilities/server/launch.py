import asyncio
from django.conf import settings
import asyncpg

from .protocol import DNSServerProtocol

def LaunchDNSServer(ip_address, port):
#    q = Queue()
#    thread = Thread(target=RunDBThread, args=(q,), daemon=True)
#    thread.start()

    while True:
        asyncio.run(UDPListener(ip_address, port),)

async def UDPListener(ip_address='127.0.0.1', port=53, xtra_loop=None):
    db_name = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    dsn = f'postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

#    print("Starting DNS UDP Server")

    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    # One protocol instance will be created to serve all
    # client requests.
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: DNSServerProtocol(dsn),
        local_addr=(ip_address, port))
    #        local_addr=('127.0.0.1', 9999))

    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()
