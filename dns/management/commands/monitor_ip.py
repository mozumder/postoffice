"""
Continously ping a target site and update DNS if current IP address changes.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests
class Command(BaseCommand):
#    args = 'mailbox rulesfile'
    help = ('Continously ping a target site and update DNS if current IP address changes..')

    def add_arguments(self, parser):
        parser.add_argument('--url',
                    action='store_true',
                    dest='url',
                    default=settings.PING_URL,
                    help='Target url to ping. URL should responds with your IP address in plain/text')
        parser.add_argument('--interval',
                    action='store_true',
                    dest='interval',
                    default=600,
                    help='Ping interval in seconds.')

    def handle(self, *args, **options):
#        usage = 'Required arguments: mailbox rulesfile'

        r = requests.head(url = options['url'])
        if r.status_code == 200:
            print(r.headers['ip'])
        else:
            print("problem!")
            
        return
