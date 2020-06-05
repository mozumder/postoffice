from multiprocessing import Process, Manager, Pool, Array, Pipe, Queue, current_process
import asyncio
import asyncpg
import functools
import time
from .query import Query
from .db import DBConnectInit
#header_format = '!H2B4H'

def worker(receive_queue, send_queue, dsn,):
#    print(multiprocessing.current_process())
    id = receive_queue.get()
    loop = asyncio.get_event_loop()
    db_pool = loop.run_until_complete(asyncpg.create_pool(dsn,init=DBConnectInit))
    while True:
        data = receive_queue.get()
        print(f'Process {id} received message')
        response = loop.run_until_complete(Query(db_pool, data))
        send_queue.put(response)

class MultiprocessorDNSServer:
    def __init__(self, dsn, processes=1):
        self.dsn = dsn
        self.processes = processes
    
    def connection_made(self, transport):
        print("DNS UDP connection created.")
        self.transport = transport
        pool = Pool(processes=self.processes)
        m = Manager()
        self.send_queue = m.Queue()
        for i in range(self.processes):
            self.send_queue.put(i)
        self.receive_queue = m.Queue()
        workers = [pool.apply_async(worker, (self.send_queue, self.receive_queue, self.dsn,)) for i in range(self.processes)]

    def connection_lost(self, exc):
        if exc == None:
            print("Connection closed.")
        else:
            print("Error. Connection closed.")

    def datagram_received(self, data, addr):
<<<<<<< HEAD
=======
        # TODO: Enable multiprocessing for new datagrams
>>>>>>> d441fc7800bf2481f99eaf2e935072d63704f41e
#        print(f'Got datagram from {addr} with length {len(data)}')
#        self.queue.put("Hello")
        self.send_queue.put(data)
        self.transport.sendto(self.receive_queue.get(), addr)


class DNSServer:
    def __init__(self, dsn, processes=1):
        self.dsn = dsn
        self.processes = processes
        self.loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(asyncpg.create_pool(
                dsn,init=DBConnectInit
                ))
        future.add_done_callback(functools.partial(self.pool_made, self))
    @staticmethod
    def pool_made(self, future):
        self.db_pool = future.result()

    def connection_made(self, transport):
        print("DNS UDP connection created.")
        self.transport = transport

    def connection_lost(self, exc):
        if exc == None:
            print("Connection closed.")
        else:
            print("Error. Connection closed.")

    @staticmethod
    def send(transport, addr, future):
        transport.sendto(future.result(), addr)
    
    def datagram_received(self, data, addr):
<<<<<<< HEAD
=======
        # TODO: Enable multiprocessing for new datagrams
>>>>>>> d441fc7800bf2481f99eaf2e935072d63704f41e
#        print(f'Got datagram from {addr} with length {len(data)}')
#        self.queue.put("Hello")
        future = asyncio.ensure_future(Query(self.db_pool, data))
        future.add_done_callback(functools.partial(self.send, self.transport, addr))
