"""
Delete Host
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import CNAME_Record, Domain

class Command(BaseCommand):
    help = ("Delete an aliased host name under a domain. This deletes a CNAME record.")

    def add_arguments(self, parser):
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help="Domain name that host is under",
            )
        parser.add_argument(
            'alias',
            nargs='?',
            action='store',
            default=None,
            help="Host name alias to be deleted",
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")
        if options['alias'] == None:
            raise CommandError("Need an Alias Name.")

        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found. Exiting')

        try:
            cname = CNAME_Record.objects.get(domain=domain, name=options['alias'])
        except:
            raise CommandError('CNAME Alias not found. Exiting')

        print(f'Deleting CNAME alias {cname}')
        cname.delete()


