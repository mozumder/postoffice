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
    # Create a new event loop for each iteration
    loop = asyncio.get_event_loop()

    # Create and start the server
    try:
        server = await loop.create_server(
                lambda: proto, host, port, reuse_port=True)
    except asyncio.CancelledError as e:
        print(f'TCP server creation received request to cancel with: {e}')
        raise asyncio.CancelledError("bad")
    except Exception as e:
        print(f"ERROR Creating TCP server: {e}")
    print(f'TCP Server {server} started and listening on port {port}')

    # Wait for an hour
    try:
        await asyncio.sleep(12)
    except asyncio.CancelledError as e:
        print(f'TCP Listener Received request to cancel with: {e}')
        server.close()
#            raise asyncio.CancelledError("TCP cancelled")
    except Exception as e:
        print(f"ERROR Running TCP server: {e}")
    finally:
        server.close()

    # Close the server
    print(f'Waiting for TCP Listener to close')
    await server.wait_closed()

    print('TCP Listener closed.')


async def UDPListener(db_pool, host='127.0.0.1', port=53, processes=1, debug=False):
    print(f'Starting UDP server on port {port}')
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    # One protocol instance will be created to serve all
    # client requests.
    try:
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: DNSProtocol(db_pool,processes,"UDP", debug),
            local_addr=(host, port), reuse_port=True)
    except asyncio.CancelledError as e:
        print(f'UDP Datagram endpoint creation received request to cancel with: {e}')
        raise asyncio.CancelledError("bad")
    except Exception as e:
        print(f"ERROR creating UDP datagram endpoint: {e}")

    print(f'UDP datagram endpoint {transport} with protocol {protocol} started and listening on port {port}')

    # Wait for some tme
    try:
        await asyncio.sleep(12)
    except asyncio.CancelledError as e:
        print(f'UDP Listener Received request to cancel with: {e}')
        transport.close()
#            raise asyncio.CancelledError("UDP cancelled")
    except Exception as e:
        print(f"ERROR Running TCP server: {e}")

    print('UDP Listener closed.')


# Function to stop the servers
def stop_servers(tcp_task, udp_task):
    print("stopping servers")
    tcp_task.cancel('Stop TCP Right Now')
    udp_task.cancel('Stop UDP Right Now')
    print("servers stopped")

async def Launcher(db_pool, host='127.0.0.1', port=53, processes=1, debug=False):
    while True:
#        print("starting udp task")
        udp_task = asyncio.create_task(UDPListener(db_pool, host, port, processes, debug))
#        print("starting tcp task")
        tcp_task = asyncio.create_task(TCPListener(db_pool, host, port, processes, debug))

        print("waiting some time before canceling both tasks")
        await asyncio.sleep(4)  # Wait for 1 hour
        stop_servers(tcp_task, udp_task)
        try:
            print('Finishing servers')
            await asyncio.gather(tcp_task, udp_task)
            print('Servers finished')
        except asyncio.CancelledError as e:
            print(f'Received request to cancel with: {e}')
            raise e
        except Exception as e:
            print(f"ERROR running tasks: {e}")
        print("Restarting servers")

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
