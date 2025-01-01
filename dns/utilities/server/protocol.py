from multiprocessing import Process, Manager, Pool, Array, Pipe, Queue, current_process
import asyncio
import asyncpg
import functools
import time
from .query import Query
#header_format = '!H2B4H'
from .db import DBConnectInit
import hexdump
import traceback

async def worker(id, receive_queue, send_queue, protocol_name, dsn, tcp, debug):
    loop = asyncio.get_event_loop()
    print(f"    - creating database pool for {protocol_name} worker {id}")
    async with asyncpg.create_pool(dsn,min_size=2, max_size=2, init=DBConnectInit) as db_pool:
        print(f"    - created database pool for {protocol_name} worker {id}")
        while True:
            print(f'  - {protocol_name} worker {id} receiving') if debug else None
            data = receive_queue.get()
            print(f'  - {protocol_name} worker {id} received message with length {len(data)}') if debug else None
            response = await Query(db_pool, data, tcp, debug)
            send_queue.put(response)

async def worker_launcher(msg):
    print(f"Launching worker")
    receive_queue, send_queue, dsn, debug = msg
    id = receive_queue.get()
    cur_process = current_process()

    tcp = True
    protocol_name = "TCP"
    print(f'  - {protocol_name} worker {id} for process {cur_process.name} (pid={cur_process.pid}) starting') if debug==True else None
    try:
        tcp_task = asyncio.create_task(worker(id, receive_queue, send_queue, protocol_name, dsn, tcp, debug))
    except Exception as e:
        print(f"ERROR running {protocol_name} worker {id}: {e}")
        print(traceback.format_exc())

    tcp = False
    protocol_name = "UDP"
    print(f'  - {protocol_name} worker {id} for process {cur_process.name} (pid={cur_process.pid}) starting') if debug==True else None
    try:
        udp_task = asyncio.create_task(worker(id, receive_queue, send_queue, protocol_name, dsn, tcp, debug))
    except Exception as e:
        print(f"ERROR running {protocol_name} worker {id}: {e}")
        print(traceback.format_exc())

#    raise Exception('some kind of error')
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

class DNSProtocol(asyncio.Protocol):
    def __init__(self, send_queue, receive_queue):
        self.send_queue = send_queue
        self.receive_queue = receive_queue
        super().__init__()
        print(f"DNSProtocol Object Initialized") 
    
    def connection_made(self, transport):
#        print(f"{self.protocol_name} DNS connection created.")
        self.transport = transport

    def oldconnection_lost(self, exc):
        if exc == None:
            print("  - Connection closed.")
        else:
            print(f"Error. Connection closed with exception {e}.")
        self.process_pool.terminate()
        print(f"  - DNSProtocol Process pool terminated")
        self.process_pool.join()
        print(f"  - DNSProtocol Process pool joined")

    def datagram_received(self, data, addr):
        print(f'Got datagram from {addr} with length {len(data)}') if self.debug else None
        self.send_queue.put(data)
#        print(f'Awaiting data back')
        return_data = self.receive_queue.get()
#        print(f'Got return data with length {len(return_data)}')
#        hexdump.hexdump(return_data)
        self.transport.sendto(return_data, addr)

    def data_received(self, data):
        print(f'Got data from with length {len(data)}') if self.debug else None
        self.send_queue.put(data)
#        print(f'Awaiting data back')
        return_data = self.receive_queue.get()
#        print(f'Got return data with length {len(return_data)}')
#        hexdump.hexdump(return_data)
        self.transport.write(return_data)
