"""
Add text string information to a host or domaim. This creates a TXT Record.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain, TXT_Record, SOURCE_SCRIPT

class Command(BaseCommand):
    help = ("Add text string information to a host or domaim. This creates a TXT Record for the domain.")

    def add_arguments(self, parser):
        parser.add_argument(
            '-ttl',
            action='store',
            default=settings.RECORD_TTL,
            type=int,
            help="Time-to-live of added record",
            )
        parser.add_argument(
            '-n','--name',
            nargs='?',
            action='store',
            default=None,
            help="Optional name for record. This is queried as if it was a host name.",
            )
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help="Domain name this record appears under",
            )
        parser.add_argument(
            'value',
            nargs='?',
            action='store',
            default=None,
            help="Text string to store",
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")
        else:
            domainname = options['domain']
        if options['value'] == None:
            raise CommandError("Need a value to store.")
        
        if options['name'] != None:
            searchname = options['name'] + "." + domainname
        else:
            searchname = domainname

        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found. Exiting')

        txt_record = TXT_Record.objects.create(domain=domain,searchdomain=domain.name, value=options['value'])
        txt_record.searchname = searchname
        txt_record.name = options['name']
        txt_record.ttl = options['ttl']
        txt_record.source = SOURCE_SCRIPT
        txt_record.save()
        print(f'Created TXT Record {txt_record} under domain {domain}.')



