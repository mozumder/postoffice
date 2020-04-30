"""
Add another IP address for a host
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain, A_Record, AAAA_Record, SOURCE_SCRIPT, MX_Record

class Command(BaseCommand):
    help = ("Add a host to a domain")

    def add_arguments(self, parser):
        parser.add_argument(
            '-ttl',
            action='store',
            default=settings.RECORD_TTL,
            type=int,
            help="Time-to-live of added A Name record",
            )
        parser.add_argument(
            '-6', '--ipv6',
            action='store',
            default=None,
            help="IPv6 Address",
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
        
        searchname = options['host'] + "." + domainname

        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found. Exiting')
        try:
            h = Host.objects.get(domain=domain,name=options['host'])
        except:
            print(f'No existing host. Existing.')
            return

        a_record = A_Record.objects.create(domain=domain, name=options['host'], ip_address = options['ip_address'])
        a_record.host = h
        a_record.searchname = searchname
        a_record.ttl = options['ttl']
        a_record.dynamic_ip = options['dynamic_ip']
        a_record.source = SOURCE_SCRIPT
        a_record.save()
        print(f'Created A Record {a_record} under domain {domain} for host {h}.')

        if options['ipv6']:
            aaaa_record = AAAA_Record.objects.create(domain=domain, name=options['host'], ip_address = options['ipv6'])
            aaaa_record.host = h
            aaaa_record.searchname = searchname
            aaaa_record.ttl = options['ttl']
            aaaa_record.source = SOURCE_SCRIPT
            aaaa_record.save()
            print(f'Created AAAA Record {aaaa_record} under domain {domain} for host {h}.')
