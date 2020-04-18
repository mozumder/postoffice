"""
Create Host
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain, A_Record, SOURCE_SCRIPT

class Command(BaseCommand):
    help = ("Create a host under a domain")

    def add_arguments(self, parser):
        parser.add_argument(
            '--ttl',
            action='store',
            default=settings.RECORD_TTL,
            help="Time-to-live of added A Name record",
            )
        parser.add_argument(
            '-dyn','--dynamic_ip',
            action='store_true',
            dest='dynamic_ip',
            default=False,
            help="Allow IP address updates with Dynamic DNS",
            )
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help="Domain name that host is under",
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
            help="Host name to be created",
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")
        else:
            domainname = options['domain']
        if options['ip_address'] == None:
            raise CommandError("Need an IP Address.")
        if options['host'] == None:
            print("Using blank host name.")
            
        fqdn = options['host'] + "." + domainname

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

        a_record, a_created = A_Record.objects.get_or_create(domain=domain, name=options['host'], ip_address = options['ip_address'])
        a_record.host = h
        a_record.fqdn = fqdn
        a_record.ttl = options['ttl']
        a_record.dynamic_ip = options['dynamic_ip']
        a_record.source = SOURCE_SCRIPT
        a_record.save()
        if a_created:
            print(f'Created A Record {a_record} under domain {domain} with host {h}.')
        else:
            print(f'A Record {a_record} under domain {domain} updated.')

