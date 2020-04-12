"""
List Domains
"""
from django.core.management.base import BaseCommand
from dns.models import Domain

class Command(BaseCommand):
    help = ('List all domains and their owners')

    def add_arguments(self, parser):
        parser.add_argument(
            '-u','--username',
            action='store',
            dest='username',
            default=None,
            help='Username of domain owner. Otherwise will show for all users',
            )

    def handle(self, *args, **options):
        records = Domain.objects.all()
        if options['username'] != None:
            records = records.filter(owner__username=options['username'])

        if records:
            for record in records:
                print(f'{record.owner}: {record}')
        else:
            print('No domains.')

