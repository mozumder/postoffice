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

def worker_launcher(msg):
    receive_queue, send_queue, dsn, tcp, debug = msg
    id = receive_queue.get()
    if tcp==True:
        protocol_name = "TCP"
    else:
        protocol_name = "UDP"
    cur_process = current_process()
    print(f'  - {protocol_name} worker {id} for process {cur_process.name} (pid={cur_process.pid}) starting') if debug==True else None
    try:
        asyncio.run(worker(id, receive_queue, send_queue, protocol_name, dsn, tcp, debug))
    except Exception as e:
        print(f"ERROR running {protocol_name} worker {id}: {e}")
        print(traceback.format_exc())

#    raise Exception('some kind of error')

class DNSProtocol(asyncio.Protocol):
    def __init__(self, dsn, processes=1, name="Default", debug=False):
        self.protocol_name = name
        self.debug = debug
        self.process_pool = Pool(processes=processes)
        m = Manager()
        self.send_queue = m.Queue()
        for i in range(processes):
            self.send_queue.put(i)
        self.receive_queue = m.Queue()
#        print(f'{dsn}')
        if name == "TCP":
            tcp = True
        else:
            tcp = False
        try:
#            results = [self.process_pool.apply_async(worker, (self.send_queue, self.receive_queue, dsn, tcp, debug)) for i in range(processes)]
            self.workers = self.process_pool.imap(worker_launcher, [[self.send_queue, self.receive_queue, dsn, tcp, debug]]*processes)
        except Exception as e:
            print(f"ERROR during worker creation: {e}")

        print(f"{name} DNSProtocol Object Initialized") 
        super().__init__()
    
    def connection_made(self, transport):
#        print(f"{self.protocol_name} DNS connection created.")
        self.transport = transport

    def connection_lost(self, exc):
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
