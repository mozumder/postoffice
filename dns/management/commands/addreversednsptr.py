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
            'name',
            nargs='?',
            action='store',
            default=None,
            help="IP Address name segments",
            )
        parser.add_argument(
            'host',
            nargs='?',
            action='store',
            default=None,
            help="Host name for reverse DNS answer",
            )

    def handle(self, *args, **options):
        if options['zone'] == None:
            raise CommandError("Need a zone (domain).")
        else:
            zone = options['zone']
        if options['host'] == None:
            raise CommandError("Need a hostname.")
        if options['name'] == None:
            raise CommandError("Need a Name.")
        
        fqdn = options['name'] + "." + zone

        hostname = options['host'].split(".")[0]
        hostdomainname = ".".join(options['host'].split(".")[1:])
        try:
            host_domain = Domain.objects.get(name__contains='%' + hostdomainname)
        except:
            host_domain = None
        try:
            zone = Domain.objects.get(name__icontains=zone)
        except:
            raise CommandError("Zone not found.")

        ptr_record, ptr_created = PTR_Record.objects.get_or_create(domain=zone, hostname=options['host'], name = fqdn)
        h = Host.objects.filter(domain=host_domain, name=hostname)
        if h:
            ptr_record.host = h[0]
        ptr_record.fqdn = fqdn
        ptr_record.ttl = options['ttl']
        ptr_record.source = SOURCE_SCRIPT
        ptr_record.save()
        if ptr_created:
            print(f'Created PTR Record {ptr_record} under zone {zone}.')
        else:
            print(f'PTR Record {ptr_record} under zone {zone} updated.')



