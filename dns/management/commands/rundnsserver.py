"""
Run a DNS server
"""
import asyncio
#from multiprocessing import Process, Manager, Pool, Array, Pipe, Queue, current_process

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.utilities.server import dns_main

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

    def handle(self, *args, **options):
        if options['ip_address'] == None:
            raise CommandError("Need a host IP address.")
        if options['port'] == None:
            raise CommandError("Need a port.")

        asyncio.run(dns_main(*args, **options))
