"""
Delete Host
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain

class Command(BaseCommand):
    help = ('Delete a host under a domain')

    def add_arguments(self, parser):
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help='Domain name that host is under',
            )
        parser.add_argument(
            'host',
            nargs='?',
            action='store',
            default=None,
            help='Host name to be deleted',
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")
        if options['host'] == None:
            raise CommandError("Need a Host Name.")

        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found. Exiting')

        try:
            host = Host.objects.get(domain=domain, name=options['host'])
        except:
            raise CommandError('Host not found. Exiting')

        print(f'Deleting host {host}')
        host.delete()

