"""
Create Host
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain, A_Record

class Command(BaseCommand):
    help = ('Create a host under a domain')

    def add_arguments(self, parser):
        parser.add_argument(
            '--ttl',
            action='store',
            default=settings.TTL,
            help='Time-to-live of added A Name record',
            )
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help='Domain name that host is under',
            )
        parser.add_argument(
            'ip_address',
            nargs='?',
            action='store',
            default=None,
            help="Host's A Record IP Address",
            )
        parser.add_argument(
            'host',
            nargs='?',
            action='store',
            default=None,
            help='Host name to be created',
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")
        if options['ip_address'] == None:
            raise CommandError("Need an IP Address.")
        if options['host'] == None:
            print("Using blank host name.")

        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found. Exiting')

        h, h_created = Host.objects.get_or_create(domain=domain,name=options['host'])
        h.save()
        if h_created:
            print(f'Created host {h} under domain {h.domain}.')
        else:
            print(f'Host {h} under domain {h.domain} already exists.')

        a_record, a_created = A_Record.objects.get_or_create(domain=domain, name=options['host'])
        a_record.host = h
        a_record.ip_address = options['ip_address']
        a_record.ttl = options['ttl']
        a_record.save()
        if a_created:
            print(f'Created A Record {a_record} under domain {domain} with host {h}.')
        else:
            print(f'A Record {a_record} under domain {domain} updated.')

