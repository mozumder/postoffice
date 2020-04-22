"""
Run a DNS server
"""
import asyncio

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.utilities.server import LaunchDNSServer

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

    def handle(self, *args, **options):
        if options['ip_address'] == None:
            raise CommandError("Need a host IP address.")
        if options['port'] == None:
            raise CommandError("Need a port.")

        LaunchDNSServer(options['ip_address'], options['port'])
