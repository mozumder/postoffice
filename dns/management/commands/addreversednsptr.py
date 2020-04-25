"""
Create reverse DNS lookup for an IP Address. This adds a PTR record.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain, PTR_Record, SOURCE_SCRIPT

class Command(BaseCommand):
    help = ("Create redirect from one hose name to another. This is an alias name for a host, and creates a ptr record")

    def add_arguments(self, parser):
        parser.add_argument(
            '-ttl',
            action='store',
            default=settings.RECORD_TTL,
            type=int,
            help="Time-to-live of added A Name record",
            )
        parser.add_argument(
            'zone',
            nargs='?',
            action='store',
            default=None,
            help='Zone (domain) that host is under. This is a name under "in-addr.arpa."',
            )
        parser.add_argument(
            'ip_address',
            nargs='?',
            action='store',
            default=None,
            help="IP Address to store",
            )
        parser.add_argument(
            'host',
            nargs='?',
            action='store',
            default=None,
            help="Host name for IP address",
            )

    def handle(self, *args, **options):
        if options['zone'] == None:
            raise CommandError("Need a zone (domain).")
        else:
            domainname = options['domain']
        if options['host'] == None:
            raise CommandError("Need an Canonical Name to alias.")
        if options['alias'] == None:
            raise CommandError("Need an Alias Name.")
        
        fqdn = options['alias'] + "." + domainname

        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found. Exiting')

        canonical_name = options['zone'] + '.' + options['domain']
        ptr_record, ptr_created = PTR_Record.objects.get_or_create(domain=domain, name=options['alias'], canonical_name = canonical_name)
        h = Host.objects.filter(domain=domain,name=options['host'])
        if h:
            ptr_record.host = h[0]
        ptr_record.fqdn = fqdn
        ptr_record.ttl = options['ttl']
        ptr_record.source = SOURCE_SCRIPT
        ptr_record.save()
        if ptr_created:
            print(f'Created ptr Record {ptr_record} under domain {domain}.')
        else:
            print(f'ptr Record {ptr_record} under domain {domain} updated.')



