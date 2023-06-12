import asyncio
from django.conf import settings
import asyncpg

from .protocol import DNSProtocol
from .db import DBConnectInit

# Echo handler for TCP connections
async def handle_tcp_client(reader, writer):
    print("handling tcp client")
    while True:
        data = await reader.read(1024)
        if not data:
            break
        writer.write(data)
        await writer.drain()
    writer.close()

async def TCPListener(db_pool, host='127.0.0.1', port=53, processes=1, debug=False):
    print(f'Starting TCP server on port {port}')
    proto = DNSProtocol(db_pool, processes, "TCP", debug)
    while True:
        # Create a new event loop for each iteration
        loop = asyncio.get_event_loop()

        # Create and start the server
        server = await loop.create_server(
                    lambda: proto, host, port, reuse_port=True)
#        print(f'Server started and listening on port {port}')

        # Wait for an hour
        await asyncio.sleep(3600)

        # Close the server
        server.close()
        await server.wait_closed()

        print('Server closed.')


async def UDPListener(db_pool, host='127.0.0.1', port=53, processes=1, debug=False):
    print(f'Starting UDP server on port {port}')
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    # One protocol instance will be created to serve all
    # client requests.
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: DNSProtocol(db_pool,processes,"UDP", debug),
        local_addr=(host, port), reuse_port=True)

# Function to stop the servers
def stop_servers(tcp_task, udp_task):
    tcp_task.cancel()
    udp_task.cancel()

async def Launcher(db_pool, host='127.0.0.1', port=53, processes=1, debug=False):
    while True:
#        print("starting udp task")
        udp_task = asyncio.create_task(UDPListener(db_pool, host, port, processes, debug))
#        print("starting tcp task")
        tcp_task = asyncio.create_task(TCPListener(db_pool, host, port, processes, debug))

#        print("waiting 1 hour")
        await asyncio.sleep(3600)  # Wait for 1 hour
        stop_servers(tcp_task, udp_task)
        print("stopped servers")

#asyncio.run(main(ip_address, port, processes,test_mode))

def LaunchDNSServer(host='127.0.0.1', port=53, processes=1, test_mode=False, debug=False, ):
    if test_mode == True:
        db_name = 'test_'+settings.DATABASES['default']['NAME']
    else:
        db_name = settings.DATABASES['default']['NAME']
    if debug == True:
        print('Turning on debug messages')
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    dsn = f'postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    asyncio.run(Launcher(dsn, host, port, processes, debug),)
