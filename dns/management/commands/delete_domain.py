"""
Delete Domain
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Domain

class Command(BaseCommand):
    help = ('Delete a domain')

    def add_arguments(self, parser):
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help='Domain name that host is under',
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")

        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found. Exiting')

        print(f'Deleting domain {domain}')
        domain.delete()


