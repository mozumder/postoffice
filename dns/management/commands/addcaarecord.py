"""
Create CAA from one hose name to another. This adds a CAA record.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain, CAA_Record, SOURCE_SCRIPT

class Command(BaseCommand):
    help = ("Create redirect from one hose name to another. This is an alias name for a host, and creates a CNAME record")

    def add_arguments(self, parser):
        parser.add_argument(
            '-ttl',
            action='store',
            default=settings.RECORD_TTL,
            type=int,
            help="Time-to-live for added record",
            )
        parser.add_argument(
            '-issuer_critical',
            action='store_true',
            default=False,
            help="Issuer critical added record",
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
            'tag',
            nargs='?',
            action='store',
            default=None,
            help="Tag name. Maxiumum 15 characters. Only allowed options now are: issue, issuewild, or iodef.",
            )
        parser.add_argument(
            'value',
            nargs='?',
            action='store',
            default=None,
            help="CAA record value string.",
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")
        else:
            domainname = options['domain']
        if options['tag'] == None:
            raise CommandError("Need a tag.")
        elif options['tag'].lower() not in ['issue', 'issuewild', 'iodef']:
            raise CommandError("Invalid tag.")
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

        caa_record = CAA_Record.objects.create(domain=domain, value=options['value'])
        caa_record.searchname = searchname
        caa_record.name = options['name']
        caa_record.ttl = options['ttl']
        caa_record.tag = options['tag'].lower()
        caa_record.value = options['value']
        caa_record.issuer_critical = options['issuer_critical']
        caa_record.source = SOURCE_SCRIPT
        caa_record.save()
        print(f'Created CAA Record {caa_record} under domain {domain}.')



