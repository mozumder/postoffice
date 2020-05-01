from multiprocessing import Pool, TimeoutError
import asyncio
import asyncpg
from .query import Query
from .db import DBConnectInit
#header_format = '!H2B4H'
class DNSServerProtocol:
    def __init__(self, dsn):
#        self.db_pool = db_pool
        self.db_pool = asyncio.get_running_loop().call_soon(asyncpg.create_pool(dsn,init=DBConnectInit))

    def connection_made(self, transport):
        print("DNS UDP connection created.")
        self.transport = transport
        if __name__ == '__main__':
            self.mp_pool = Pool(processes=8)

    def connection_lost(self, exc):
        if exc == None:
            print("Connection closed.")
        else:
            print("Error. Connection closed.")

    def datagram_received(self, data, addr):
        # TODO: Enable multiprocessing for new datagrams
#        print(f'Got datagram from {addr} with length {len(data)}')
        future = asyncio.ensure_future(Query(self.db_pool,data, addr, self.transport))

