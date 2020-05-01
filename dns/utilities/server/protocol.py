from multiprocessing import Process, Pool, Array, Pipe, Queue
import asyncio
import asyncpg
import functools
import time
from .query import Query
from .db import DBConnectInit
#header_format = '!H2B4H'


class DNSServerProtocol:


    def __init__(self, dsn, processes=1):
        self.dsn = dsn
        self.processes = processes
        
    @staticmethod
    def done_cb(obj, future):
        obj.db_pool = future.result()
    
    @staticmethod
    def f(receive, send):
        while True:
            obj = receive.get()
            send.put(obj)
#          pool, data, addr, transport = a.recv()
#            future = asyncio.ensure_future(Query(*obj))

    def connection_made(self, transport):
        print("DNS UDP connection created.")
        self.transport = transport
        loop = asyncio.get_running_loop()
        future = asyncio.ensure_future(asyncpg.create_pool(self.dsn,init=DBConnectInit))
        future.add_done_callback(functools.partial(self.done_cb, self))
        print(__name__)
        self.send_queue = Queue()
        self.receive_queue = Queue()
        a = Array('i', [0], lock=False)
        self.p = Process(target=self.f, args=(self.send_queue,self.receive_queue,))
        self.p.start()


    def connection_lost(self, exc):
        if exc == None:
            print("Connection closed.")
        else:
            print("Error. Connection closed.")

    def datagram_received(self, data, addr):
        # TODO: Enable multiprocessing for new datagrams
#        print(f'Got datagram from {addr} with length {len(data)}')
#        self.queue.put("Hello")
        self.send_queue.put((data,addr))
        print(self.receive_queue.get())
