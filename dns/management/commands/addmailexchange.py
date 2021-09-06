"""
Create a mail exchange for a domain. This adds an MX record.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain, MX_Record, SOURCE_SCRIPT

class Command(BaseCommand):
    help = ("""Create a mail exchange for a domain. This adds an MX record.

When someone sends an email to a domain, they look up the the mail exchange hostname for the domain, and sends mail to port 25 on that mail exchange host.
""")

    def add_arguments(self, parser):
        parser.add_argument(
            '-ttl',
            action='store',
            default=settings.RECORD_TTL,
            help="Time-to-live of added A Name record",
            )
        parser.add_argument(
            'domain',
            nargs='?',
            action='store',
            default=None,
            help="Domain name for mail exchange",
            )
        parser.add_argument(
            'host',
            nargs='?',
            action='store',
            default=None,
            help="Hostname that serves as mail exchange. Can be outside of the domain if given with a full domain name",
            )
        parser.add_argument(
            'priority',
            nargs='?',
            action='store',
            default=0,
            type=int,
            help="Priority level for email server. Highest priority is 0.",
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")
        else:
            domainname = options['domain']
        if options['host'] == None:
            raise CommandError("Need an Hostname that serves as mail exhcnage.")
        
        try:
            domain = Domain.objects.get(name=options['domain'])
        except:
            raise CommandError('Domain not found. Exiting')

        mx_record, mx_created = MX_Record.objects.get_or_create(domain=domain,searchdomain=domain.name, name=domain.name, hostname = options['host'])
        h = Host.objects.filter(domain=domain,name=options['host'])
        if h:
            cname_record.host = h[0]
        mx_record.searchname = domain.name
        mx_record.ttl = options['ttl']
        mx_record.priority = options['priority']
        mx_record.source = SOURCE_SCRIPT
        mx_record.save()
        if mx_created:
            print(f'Created MX Record {mx_record} under domain {domain}.')
        else:
            print(f'MX Record {mx_record} under domain {domain} updated.')


