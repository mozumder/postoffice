"""
Create Domain
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings

from dns.models import Domain, A_Record

class Command(BaseCommand):
    help = ('Create a domain with username as its owner')

    def add_arguments(self, parser):
        parser.add_argument(
            '-u','--username',
            action='store',
            dest='username',
            default=None,
            help='Username of domain owner. Otherwise will use first user',
            )
        parser.add_argument(
            '--ttl',
            action='store',
            dest='ttl',
            default=settings.RECORD_TTL,
            help='Time-to-live of added A Name record',
            )
        parser.add_argument(
            '-dyn','--dynamic_ip',
            action='store_true',
            dest='dynamic_ip',
            default=False,
            help='Allow IP address updates with Dynamic DNS',
            )
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            dest='domain',
            default=None,
            help='Domain name to be created',
            )
        parser.add_argument(
            'ip_address',
            nargs='?',
            action='store',
            default=None,
            help="Domain's A Record IP Address",
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")
        if options['ip_address'] == None:
            raise CommandError("Need an IP Address.")
        if options['username'] == None:
            user = User.objects.all()[0]
            print(f'Using default user: {user}')
        else:
            user = User.objects.get(username=options['username'])

        d, d_created = Domain.objects.get_or_create(owner=user,name=options['domain'])
        d.save()
        if d_created:
            print(f'Created domain {d} with owner {d.owner}.')
        else:
            print(f'Domain {d} with owner {d.owner} already exists.')

        a_record, a_created = A_Record.objects.get_or_create(domain=d,name=None)
        a_record.host = None
        a_record.ip_address = options['ip_address']
        a_record.ttl = options['ttl']
        a_record.dynamic_ip = options['dynamic_ip']
        a_record.save()
        if a_created:
            print(f'Created A Record {a_record} under domain {d}.')
        else:
            print(f'A Record {a_record} under domain {d} updated.')

