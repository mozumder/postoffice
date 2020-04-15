"""
Continously ping a target site and update DNS if current IP address changes.
"""
import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.management.utilities import DynamicDNSManager

class Command(BaseCommand):

    help = ("Continously ping a target site and update DNS if current IP address changes.")

    def add_arguments(self, parser):
        parser.add_argument(
            '-i', '--interval',
            action='store',
            type=int,
            default=settings.IP_PING_INTERVAL,
            help="Ping interval in seconds.")
        parser.add_argument(
            'ping_url',
            action='store',
            default=settings.IP_PING_URL,
            help="Target url to ping. URL should responds with your IP address in plain text")

    def handle(self, *args, **options):
        if options['ping_url'] == None:
            raise CommandError("Need a URL to ping.")

        while DynamicDNSManager.update(options['ping_url']) != 2:
            time.sleep(options['interval'])
