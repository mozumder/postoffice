import asyncio
import logging
import asyncpg
from queue import Empty
from .query import Query
#header_format = '!H2B4H'
from .db import DBConnectInit
import hexdump
import traceback

logger = logging.getLogger("dnsserver")

async def worker(id, tcp, receive_queue, send_queue, db_pool):
    if tcp == True:
        type = "TCP"
    else:
        type = "UDP"
    try:
        logger.debug(f'{type} worker {id} receiving messages') 
        logger.debug(f'receive is empty: {receive_queue.empty()}  qsize: {receive_queue.qsize()}') 
        logger.debug(f'send is empty: {send_queue.empty()}  qsize: {send_queue.qsize()}') 
        data = await receive_queue.get()
        logger.debug(f'{type} worker {id} received message with length {len(data)}')
        try:
            print('here 1')
            response = await Query(db_pool, data, tcp)
            print('here 2')
        except Exception:
            traceback.print_exc()
        finally:
            logger.debug(f'{type} worker {id} received database response with length {len(response)}')
            await send_queue.put(response)
    except asyncio.CancelledError as e:
        logger.debug(f"Stopping {type} task {id}")
    except Empty:
        pass
    except Exception:
        traceback.print_exc()

async def task_monitor(monitored_task, control_queue, id):
    while True:
        control = await control_queue.get()
        if control == "stop":
            monitored_task.cancel()
            break

async def worker_launcher(msg):
    id, control_queue, status_queue, udp_receive_queue, udp_send_queue, tcp_receive_queue, tcp_send_queue, dsn, loglevel = msg
    logger.setLevel(loglevel)
    logger.debug(f'Process {id} launched')
    async with asyncpg.create_pool(dsn,min_size=2, max_size=2, init=DBConnectInit) as db_pool:
        tcp_worker_task = asyncio.create_task(worker(id, True, tcp_receive_queue, tcp_send_queue, db_pool))
        udp_worker_task = asyncio.create_task(worker(id, False, udp_receive_queue, udp_send_queue, db_pool))
        tcp_monitor_task = asyncio.create_task(task_monitor(tcp_worker_task, control_queue, id))
        udp_monitor_task = asyncio.create_task(task_monitor(udp_worker_task, control_queue, id))
        result = await asyncio.gather(tcp_worker_task,udp_worker_task,tcp_monitor_task,udp_monitor_task)


# Echo handler for TCP connections
async def handle_dns_query(reader, writer, tcp_send_queue, tcp_receive_queue):
    logger.debug("handling tcp client")
    while True:
        data = await reader.read(1024)
        if not data:
            break
        logger.debug(f'Got TCP data with length {len(data)}')
        await tcp_send_queue.put(data)
        logger.debug(f'Awaiting data back')
        return_data = await tcp_receive_queue.get()
        logger.debug(f'Got return data with length {len(return_data)}')
#        hexdump.hexdump(return_data)
        writer.write(return_data)
        await writer.drain()
    writer.close()

class DNSProtocol(asyncio.Protocol):
    def __init__(self, send_queue, receive_queue):
        self.send_queue = send_queue
        self.receive_queue = receive_queue
        self.loop = asyncio.get_event_loop()
        logger.debug(f"DNSProtocol Object Initialized") 
    
    def connection_made(self, transport):
        logger.debug(f'Got UDP port')
        self.transport = transport

    def datagram_received(self, data, addr):
        logger.debug(f'Got UDP datagram from {addr} with length {len(data)}')
        self.loop.create_task(self.handle_incoming_packet(data, addr))

    async def handle_incoming_packet(self, data, addr):
        # echo back the message, but 2 seconds later
        logger.debug(data)
        logger.debug(f'Querying database')
        try:
            await self.receive_queue.put(data)
        except Exception:
            traceback.print_exc()

        logger.debug(f'Awaiting data back')
        try:
            return_data = await self.send_queue.get()
        except Exception:
            traceback.print_exc()

        logger.debug(f'Got return data with length {len(return_data)}')
#        hexdump.hexdump(return_data)
        self.transport.sendto(return_data, addr)
