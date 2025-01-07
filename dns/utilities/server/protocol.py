import os
import asyncio
from queue import Empty
import logging
import traceback

import hexdump
import asyncpg

from .query import Query
from .db import DBConnectInit

#header_format = '!H2B4H'

async def worker(msg: list):
    id, control_queue, status_queue, udp_receive_queue, udp_send_queue, tcp_receive_queue, tcp_send_queue, dsn = msg
    logger = logging.getLogger("dnsserver")
    tcp = False
    pid = os.getpid()
    logger.debug(f'Process {pid} started')

    async with asyncpg.create_pool(dsn,min_size=2, max_size=2, init=DBConnectInit) as db_pool:
        while True:
            try:
                data = udp_receive_queue.get(timeout=1)
                logger.debug(f'worker received msg')
                response = await Query(db_pool, data, tcp)
                udp_send_queue.put(response)
            except Empty:
                pass
            except Exception:
                traceback.print_exc()

            try:
                msg = control_queue.get(block=False)
                if msg == "stop":
                    # Process the item
                    logger.debug("Processing:", msg)
                    status_queue.put(f"stopped")
                    break
            except Empty:
                pass
            except Exception:
                traceback.print_exc()
    logger.debug(f'Process {pid} stopped')


async def workerx(id, tcp, receive_queue, send_queue, db_pool):
    logger = logging.getLogger("dnsserver")
    if tcp == True:
        type = "TCP"
    else:
        type = "UDP"
    logger.debug(f'{type} worker {id} receiving messages') 
    while True:
        try:
            logger.debug(f'receive is empty: {receive_queue.empty()}  qsize: {receive_queue.qsize()}') 
            logger.debug(f'send is empty: {send_queue.empty()}  qsize: {send_queue.qsize()}') 
            data = receive_queue.get()
            logger.debug(f'{type} worker {id} received message with length {len(data)}')
            try:
                logger.debug('here 1')
                response = await Query(db_pool, data, tcp, True)
                logger.debug('here 2')
            except Empty:
                pass
            except Exception:
                traceback.print_exc()
            finally:
                logger.debug(f'{type} worker {id} received database response with length {len(response)}')
                send_queue.put(response)
        except asyncio.CancelledError as e:
            logger.debug(f"Stopping {type} task {id}")
            raise
        except Empty:
            pass
        except Exception:
            traceback.print_exc()

async def task_monitor(tcp_worker_task, udp_worker_task, control_queue, status_queue, id):
    logger = logging.getLogger("dnsserver")
    logger.debug(f"Monitoring worker {id}")
    while True:
        msg = control_queue.get()
        if msg == "stop":
            logger.debug(f"got stop msg to cancel worker {id}")
            udp_worker_task.cancel()
            logger.debug(f"canceling udp_worker_task")
            try:
                await udp_worker_task
            except asyncio.CancelledError:
                logger.debug(f"canceled udp_worker_task {id}")
            except Exception:
                traceback.print_exc()

            tcp_worker_task.cancel()
            logger.debug(f"canceling tcp_worker_task")
            try:
                await tcp_worker_task
            except asyncio.CancelledError:
                logger.debug(f"canceled tcp_worker_task {id}")
            except Exception:
                traceback.print_exc()

            status_queue.put(f'stopped {id}')
        else:
            logger.debug(f"weird msg {msg}")

async def worker_task_launcher(id, control_queue, status_queue, udp_receive_queue, udp_send_queue, tcp_receive_queue, tcp_send_queue, dsn):
    logger = logging.getLogger("dnsserver")
    logger.debug(f'Waiting for control msg')
    async with asyncpg.create_pool(dsn,min_size=2, max_size=2, init=DBConnectInit) as db_pool:
        async with asyncio.TaskGroup() as tg:
            tcp_worker_task = tg.create_task(worker(id, True, tcp_receive_queue, tcp_send_queue, db_pool))
            udp_worker_task = tg.create_task(worker(id, False, udp_receive_queue, udp_send_queue, db_pool))
            monitor_task = tg.create_task(task_monitor(tcp_worker_task, udp_worker_task, control_queue, status_queue, id))

async def worker_launcher(msg):
    id, control_queue, status_queue, udp_receive_queue, udp_send_queue, tcp_receive_queue, tcp_send_queue, dsn = msg
    logger = logging.getLogger("dnsserver")
    pid = os.getpid()
    logger.debug(f'Process {pid} started')
    async with asyncpg.create_pool(dsn,min_size=2, max_size=2, init=DBConnectInit) as db_pool:
        async with asyncio.TaskGroup() as tg:
            tcp_worker_task = tg.create_task(worker(id, True, tcp_receive_queue, tcp_send_queue, db_pool))
            udp_worker_task = tg.create_task(worker(id, False, udp_receive_queue, udp_send_queue, db_pool))
            monitor_task = tg.create_task(task_monitor(tcp_worker_task, udp_worker_task, control_queue, status_queue, id))
    logger.debug(f'Process {pid} finished')

# Echo handler for TCP connections
async def handle_dns_query(reader, writer, tcp_send_queue, tcp_receive_queue):
    logger = logging.getLogger("dnsserver")
    logger.debug("handling tcp client")
    while True:
        data = await reader.read(1024)
        if not data:
            break
        logger.debug(data)
        logger.debug(f'Got TCP data with length {len(data)}')
        tcp_send_queue.put(data)
        logger.debug(f'Awaiting data back')
        return_data = tcp_receive_queue.get()
        logger.debug(f'Got return data with length {len(return_data)}')
#        hexdump.hexdump(return_data)
        writer.write(return_data)
        await writer.drain()
    writer.close()

class DNSProtocol(asyncio.Protocol):
    def __init__(self, send_queue, receive_queue):
        logger = logging.getLogger("dnsserver")
        self.send_queue = send_queue
        self.receive_queue = receive_queue
        self.loop = asyncio.get_event_loop()
        self.transports = {}
        logger.debug(f"DNSProtocol Object Initialized") 
    
    def connection_made(self, transport):
        logger = logging.getLogger("dnsserver")
        logger.debug(f'Got UDP port')
        self.transport = transport

    def datagram_received(self, data, addr):
        logger = logging.getLogger("dnsserver")
        logger.debug(f'Got UDP datagram from {addr} with length {len(data)}')
        self.loop.create_task(self.handle_incoming_packet(self.transport, data, addr))

    async def handle_incoming_packet(self, transport, data, addr):
        logger = logging.getLogger("dnsserver")
        logger.debug(data)
        logger.debug(f'Querying database')
        try:
            self.receive_queue.put(data)
        except Exception:
            traceback.print_exc()

        logger.debug(f'Awaiting data back')
        try:
            return_data = self.send_queue.get()
        except Exception:
            traceback.print_exc()

        logger.debug(f'Got return data with length {len(return_data)}')
#        hexdump.hexdump(return_data)
        transport.sendto(return_data, addr)


async def udp_server(receive_queue, send_queue, ip_address, port):
    logger = logging.getLogger("dnsserver")
    sock = await asyncudp.create_socket(local_addr=(ip_address, port))
    while True:
        data, addr = await sock.recvfrom()
        logger.debug(data)
        logger.debug(f'Querying database')
        try:
            receive_queue.put(data)
        except Exception:
            traceback.print_exc()

        logger.debug(f'Awaiting data back')
        try:
            return_data = send_queue.get()
        except Exception:
            traceback.print_exc()

        logger.debug(f'Got return data with length {len(return_data)}')
#        hexdump.hexdump(return_data)
        sock.sendto(data, addr)
