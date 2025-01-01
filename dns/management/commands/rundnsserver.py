"""
Run a DNS server
"""
import asyncio
#from multiprocessing import Process, Manager, Pool, Array, Pipe, Queue, current_process
from multiprocessing import Pool, Manager
from concurrent.futures import ProcessPoolExecutor

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.utilities.server import LaunchDNSServer
from dns.utilities.server import worker_launcher

class Command(BaseCommand):

    help = ("Run a DNS server.")

    def add_arguments(self, parser):
        parser.add_argument(
            '-ip', '--ip_address',
            action='store',
            type=str,
            default='127.0.0.1',
            help="Host address to run DNS server protocol.")
        parser.add_argument(
            '-p', '--port',
            action='store',
            default=53,
            help="Port number to run DNS server protocol")
        parser.add_argument(
            '-proc', '--processes',
            action='store',
            type=int,
            default=1,
            help="Number of concurrent processes to run")
        parser.add_argument(
            '-thr', '--threads',
            action='store',
            type=int,
            default=1,
            help="Number of threads per processes")
        parser.add_argument(
            '-t', '--test_mode',
            action='store_true',
            default=False,
            help="Run with test database.")
        parser.add_argument(
            '-d', '--debug',
            action='store_true',
            default=False,
            help="Turn on debug messages.")


    async def handle_echo(self, reader, writer):
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        print(f"Received {message!r} from {addr!r}")

        print(f"Send: {message!r}")
        writer.write(data)
        await writer.drain()

        print("Close the connection")
        writer.close()
        await writer.wait_closed()

    async def main(self, *args, **options):
        print('here 5')

        server = await asyncio.start_server(
            self.handle_echo, options['ip_address'], options['port'])

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()

    def handle(self, *args, **options):
        if options['ip_address'] == None:
            raise CommandError("Need a host IP address.")
        if options['port'] == None:
            raise CommandError("Need a port.")

        if options['test_mode'] == True:
            db_name = 'test_'+settings.DATABASES['default']['NAME']
        else:
            db_name = settings.DATABASES['default']['NAME']
        if options['debug'] == True:
            print('Turning on debug messages')
        db_user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        db_host = settings.DATABASES['default']['HOST']
        db_port = settings.DATABASES['default']['PORT']
        dsn = f'postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

        self.process_pool = Pool(processes=options['processes'])
        m = Manager()
        self.send_queue = m.Queue()
        for i in range(options['processes']):
            self.send_queue.put(i)
        self.receive_queue = m.Queue()

        opts = [self.send_queue, self.receive_queue, dsn, options['debug']]

#        self.workers = self.process_pool.imap(self.main_launcher, opts)
        asyncio.run(self.main(*args, **options))
        print('here 2')
#        try:
#            results = [self.process_pool.apply_async(worker, (self.send_queue, self.receive_queue, dsn, tcp, debug)) for i in range(processes)]
#            self.workers = self.process_pool.imap(worker_launcher, [[self.send_queue, self.receive_queue, dsn,options['debug']]]*options['processes'])
#            with concurrent.futures.ProcessPoolExecutor() as pool:
#                result = await loop.run_in_executor(
#                    pool, worker_launcher, [self.send_queue, self.receive_queue, dsn,options['debug']])
#                print('custom process pool', result)
#        except Exception as e:
#            print(f"ERROR during TCP worker creation: {e}")

#        asyncio.run(self.main(*args, **options))

#        LaunchDNSServer(options['ip_address'], options['port'], options['processes'], options['test_mode'], options['debug'])


