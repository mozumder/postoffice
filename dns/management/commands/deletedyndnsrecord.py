"""
Delete Dynamic DNS authentication login for an A Record
"""
import secrets

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain, A_Record, DynamicDNS

class Command(BaseCommand):
    help = ("Create Dynamic DNS authentication login for an A Record")

    def add_arguments(self, parser):
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help="The A record's domain",
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

        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found.')

        try:
            a_record = A_Record.objects.get(domain=domain, name=options['name'])
        except:
            raise CommandError('A Record not found.')

        try:
            dyndns = DynamicDNS.objects.get(a_record)
        except:
            raise CommandError('Dynamic DNS record not found. Exiting')

        print(f'Deleting Dyanmic DNS record {dyndns}')
        dyndns.delete()



