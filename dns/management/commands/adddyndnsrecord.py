"""
Create Dynamic DNS authentication login for an A Record
"""
import secrets

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain, A_Record, DynamicDNS

class Command(BaseCommand):
    help = ("Create Dynamic DNS authentication login for an A Record")

    def add_arguments(self, parser):
        parser.add_argument(
            '-p','--password',
            action='store',
            default=None,
            help="Password for Dynamic DNS record",
            )
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help="The A record's domain",
            )
        parser.add_argument(
            'dynamicdns_id',
            nargs='?',
            action='store',
            default=None,
            help="Dynamic DNS Record ID",
            )
        parser.add_argument(
            'name',
            nargs='?',
            action='store',
            default=None,
            help="The domain's A record name",
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain.")
        if options['dynamicdns_id'] == None:
            raise CommandError("Need a Dynamic DNS ID.")

        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found.')

        try:
            a_record = A_Record.objects.get(domain=domain, name=options['name'])
        except:
            raise CommandError('A Record not found.')
        if options['password'] == None:
            password = secrets.token_urlsafe(11)
        else:
            password = options['password']
        
        dyndns, dyndns_created = DynamicDNS.objects.get_or_create(a_record=a_record)
        dyndns.dyndns_id = options['dynamicdns_id']
        dyndns.password = password
        dyndns.save()
        if dyndns_created:
            print(f'Created Dynamic DNS {dyndns} with password {dyndns.password}')
        else:
            print(f'Updated Dynamic DNS {dyndns} with password {dyndns.password}')



