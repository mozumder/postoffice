import os
import asyncio
from queue import Empty
import logging
import traceback
import uuid

import hexdump
import asyncpg

from .query import Query
from .db import DBConnectInit

#header_format = '!H2B4H'

async def worker(msg: list):
    control_queue, status_queue, receive_queue, send_queue, dsn = msg
    logger = logging.getLogger("dnsserver")
    tcp = False
    pid = os.getpid()
    logger.debug(f'Process {pid} started')

    async with asyncpg.create_pool(dsn,min_size=2, max_size=2, init=DBConnectInit) as db_pool:
        while True:
            try:
                id, data, tcp = receive_queue.get(timeout=1)
                logger.debug(f'worker received msg')
                response = await Query(db_pool, data, tcp)
                send_queue.put([id, response, tcp])
            except Empty:
                pass
            except Exception:
                traceback.print_exc()

            try:
                msg = control_queue.get(block=False)
                if msg == "stop":
                    # Process the item
                    logger.debug(f"Processing: {msg}")
                    status_queue.put(f"stopped")
                    break
            except Empty:
                pass
            except Exception:
                traceback.print_exc()
    logger.debug(f'Process {pid} stopped')


class DNSProtocol(asyncio.Protocol):
    def __init__(self, send_queue, receive_queue):
        logger = logging.getLogger("dnsserver")
        self.send_queue = send_queue
        self.receive_queue = receive_queue
        self.loop = asyncio.get_event_loop()
        self.transports = {}
        self.msg_ids = {}
        logger.debug(f"DNSProtocol Object Initialized") 
    
    def connection_made(self, transport):
        logger = logging.getLogger("dnsserver")
        logger.debug(f'Got UDP port')
        self.transport = transport

    def datagram_received(self, data, addr):
        logger = logging.getLogger("dnsserver")
        logger.debug(f'Got UDP datagram from {addr} with length {len(data)}')
        id = uuid.uuid4()
        self.msg_ids[id] = [data, addr]
        self.loop.create_task(self.handle_incoming_packet(id, self.transport, data, addr))

    async def handle_incoming_packet(self, id, transport, data, addr):
        logger = logging.getLogger("dnsserver")
        logger.debug(data)
        logger.debug(f'Querying database')
        try:
            self.receive_queue.put([id, data, False])
        except Exception:
            traceback.print_exc()

        logger.debug(f'Awaiting data back')
        try:
            id, return_data, tcp = self.send_queue.get()
        except Exception:
            traceback.print_exc()

        logger.debug(f'Got return data with length {len(return_data)}')
#        hexdump.hexdump(return_data)
        transport.sendto(return_data, addr)

