import asyncio
from .query import Query
#header_format = '!H2B4H'
class DNSServerProtocol:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print(f'Got datagram from {addr} with length {len(data)}')
        future = asyncio.ensure_future(Query(self.db_pool,data, addr, self.transport))

