"""
Create Host
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain, CNAME_Record, SOURCE_SCRIPT

class Command(BaseCommand):
    help = ("Add an alias name for a host. This creates a CNAME record")

    def add_arguments(self, parser):
        parser.add_argument(
            '--ttl',
            action='store',
            default=settings.RECORD_TTL,
            help="Time-to-live of added A Name record",
            )
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help="Domain name that host is under",
            )
        parser.add_argument(
            'canonical_hostname',
            nargs='?',
            action='store',
            default=None,
            help="Canonical name of the host",
            )
        parser.add_argument(
            'alias',
            nargs='?',
            action='store',
            default=None,
            help="Alias name of the host to be created",
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")
        else:
            domainname = options['domain']
        if options['canonical_hostname'] == None:
            raise CommandError("Need an Canonical Name to alias.")
        if options['alias'] == None:
            raise CommandError("Need an Alias Name.")
            
        fqdn = options['alias'] + "." + domainname

        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found. Exiting')


        cname_record, cname_created = CNAME_Record.objects.get_or_create(domain=domain, name=options['alias'], canonical_name = options['canonical_hostname'])
        h = Host.objects.filter(domain=domain,name=options['canonical_hostname'])
        if h:
            cname_record.host = h[0]
        cname_record.fqdn = fqdn
        cname_record.ttl = options['ttl']
        cname_record.source = SOURCE_SCRIPT
        cname_record.save()
        if cname_created:
            print(f'Created CNAME Record {cname_record} under domain {domain}.')
        else:
            print(f'CNAME Record {cname_record} under domain {domain} updated.')


