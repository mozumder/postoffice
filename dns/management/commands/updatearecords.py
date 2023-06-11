"""
Set A Record IP Address
"""
from django.core.management.base import BaseCommand, CommandError

from dns.models import Domain, A_Record

class Command(BaseCommand):
    help = ("Create a a host under a domain")

    def add_arguments(self, parser):
        parser.add_argument(
            '--ttl',
            action='store',
            default=None,
            help="Time-to-live",
            )
        parser.add_argument(
            '--ip',
            action='store',
            default=None,
            help="IP Address",
            )
        parser.add_argument(
            '-dynamic','--dynamic_ip',
            action='store_true',
            dest='dynamic_ip',
            default=None,
            help="Allow IP address updates with Dynamic DNS",
            )
        parser.add_argument(
            '-static','--static_ip',
            action='store_false',
            dest='dynamic_ip',
            default=None,
            help="Disallow IP address updates with Dynamic DNS",
            )
        parser.add_argument(
            '-a', '--all',
            action='store_true',
            default=False,
            help="Update all A Records in a domain",
            )
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help="Domain to update",
            )
        parser.add_argument(
            'name',
            nargs='?',
            action='store',
            default=None,
            help="A Record name to update. Leave blank to update only the domain's A Record.",
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")
        if options['ip'] == None and options['ttl'] == None and options['dynamic_ip'] == None:
            raise CommandError("No IP Address, TTL, or Dynamic IP setting.")
        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found.')

        if options['all'] == True:
            records = A_Record.objects.filter(domain=domain)
        else:
            records = A_Record.objects.filter(domain=domain, name=options['name'])

        if records:
            for record in records:
                if options['ip'] != None:
                    record.ip_address = options['ip']
                if options['ttl'] != None:
                    record.ttl = options['ttl']
                if options['dynamic_ip'] != None:
                    record.dynamic_ip = options['dynamic_ip']
                record.save()
                print(f'A Record {record} updated.')
        else:
            print('No A Records.')




