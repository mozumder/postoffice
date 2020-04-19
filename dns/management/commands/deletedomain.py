"""
Delete Domain
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Domain, NS_Record, SOA_Record, A_Record

class Command(BaseCommand):
    help = ("Delete a domain")

    def add_arguments(self, parser):
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help="Domain name that host is under",
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")

        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found. Exiting')

        ns_records = NS_Record.objects.filter(domain=domain)
        for ns_record in ns_records:
            print(f'Deleting NS Record {ns_record}')
            ns_record.delete()
        soa_records = SOA_Record.objects.filter(domain=domain)
        for soa_record in soa_records:
            print(f'Deleting SOA Record {soa_record}')
            soa_record.delete()
        a_records = A_Record.objects.filter(domain=domain)
        for a_record in a_records:
            print(f'Deleting A Record {a_record}')
            a_record.delete()

        print(f'Deleting domain {domain}')
        domain.delete()


