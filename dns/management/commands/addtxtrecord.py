"""
Create redirect from one hose name to another. This adds a CNAME record.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain, TXT_Record, SOURCE_SCRIPT

class Command(BaseCommand):
    help = ("Create redirect from one hose name to another. This is an alias name for a host, and creates a CNAME record")

    def add_arguments(self, parser):
        parser.add_argument(
            '-ttl',
            action='store',
            default=settings.RECORD_TTL,
            type=int,
            help="Time-to-live of added A Name record",
            )
        parser.add_argument(
            '-n','--name',
            nargs='?',
            action='store',
            default=None,
            help="Name for record. This is similar to a host name and is optional for the domain.",
            )
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help="Domain name that record is applied",
            )
        parser.add_argument(
            'value',
            nargs='?',
            action='store',
            default=None,
            help="String for the value of the TXT record",
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")
        else:
            domainname = options['domain']
        if options['value'] == None:
            raise CommandError("Need a value to store.")
        
        if options['name'] != None:
            fqdn = options['name'] + "." + domainname
        else:
            fqdn = domainname

        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found. Exiting')

        txt_record = TXT_Record.objects.create(domain=domain, value=options['value'])
        txt_record.fqdn = fqdn
        txt_record.name = options['name']
        txt_record.ttl = options['ttl']
        txt_record.source = SOURCE_SCRIPT
        txt_record.save()
        print(f'Created TXT Record {txt_record} under domain {domain}.')



