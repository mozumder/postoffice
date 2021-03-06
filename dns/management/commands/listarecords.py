"""
List A Records
"""
from django.core.management.base import BaseCommand

from dns.models import A_Record

class Command(BaseCommand):
    help = ("List all A Records and their owners")

    def add_arguments(self, parser):
        parser.add_argument(
            '-d','--domain',
            action='store',
            default=None,
            help="Domain to list. Otherwise will show for all domains of a user",
            )
        parser.add_argument(
            '-u','--username',
            action='store',
            default=None,
            help="Username of domain owner. Otherwise will show for all users",
            )

    def handle(self, *args, **options):
        records = A_Record.objects.all()
        if options['domain'] != None:
            records = records.filter(domain__name=options['domain'])
        if options['username'] != None:
            records = records.filter(domain__owner__username=options['username'])

        if records:
            for record in records:
                print(f'{record.domain.owner}: {record} {record.ip_address} ttl: {record.ttl}s')
        else:
            print('No A Records.')


