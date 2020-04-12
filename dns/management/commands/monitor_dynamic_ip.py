"""
Continously ping a target site and update DNS if current IP address changes.
"""
import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.management.utilities import DynamicDNSManager

class Command(BaseCommand):

    help = ('Continously ping a target site and update DNS if current IP address changes.')

    def add_arguments(self, parser):
        parser.add_argument(
                    '-p', '--ping_url',
                    action='store',
                    default=settings.IP_PING_URL,
                    help='Target url to ping. URL should responds with your IP address in plain text')
        parser.add_argument(
                    '-i', '--interval',
                    action='store',
                    type=int,
                    default=settings.IP_PING_INTERVAL,
                    help='Ping interval in seconds.')
        parser.add_argument(
                    '-e', '--dynamic_dns_update_endpoint',
                    action='store',
                    default=settings.DYNDNS_ENDPOINT,
                    help='URL Endpoint to update DNS record')
        parser.add_argument(
                    '-u', '--dynamic_dns_update_username',
                    action='store',
                    default=settings.DYNDNS_USERNAME,
                    help='Dyanamic DNS record username')

    def handle(self, *args, **options):
        if options['ping_url'] == None:
            raise CommandError("Need a URL to ping.")
        if options['dynamic_dns_update_endpoint'] == None:
            raise CommandError("Need a Dynamic DNS URL endpoint to update IP address.")
        if options['dynamic_dns_update_username'] == None:
            raise CommandError("Need a Dynamic DNS Username to update IP address.")

        while True:
            DynamicDNSManager.update(options)
            time.sleep(options['interval'])
