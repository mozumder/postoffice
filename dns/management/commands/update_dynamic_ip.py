"""
Continously ping a target site and update DNS if current IP address changes.
"""
import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.management.utilities import DynamicDNSManager

class Command(BaseCommand):

    help = ("Ping a target URL and update DNS record if current IP address is different.")

    def add_arguments(self, parser):
        parser.add_argument(
                    'ping_url',
                    action='store',
                    default=settings.IP_PING_URL,
                    help="Target url to ping. URL should responds with your IP address in plain text")

    def handle(self, *args, **options):
        if options['ping_url'] == None:
            raise CommandError("Need a URL to ping.")
        if options['dynamic_dns_update_endpoint'] == None:
            raise CommandError("Need a Dynamic DNS URL endpoint to update IP address.")
        if options['dynamic_dns_update_username'] == None:
            raise CommandError("Need a Dynamic DNS Username to update IP address.")

        DynamicDNSManager.update(options['ping_url'])

