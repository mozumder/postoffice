"""
Create redirect from one hose name to another. This adds a CNAME record.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dns.models import Host, Domain, SRV_Record, SOURCE_SCRIPT

class Command(BaseCommand):
    help = ("Create redirect from one hose name to another. This is an alias name for a host, and creates a CNAME record")

    def add_arguments(self, parser):
        parser.add_argument(
            '-ttl',
            action='store',
            default=settings.RECORD_TTL,
            type=int,
            help="Time-to-live of added A Name record",
            )
        parser.add_argument(
            '-pri', '--priority',
            action='store',
            default=0,
            type=int,
            help="The relative Priority of this service (range 0 - 65535). Lowest is highest priority, usage is the same as the MX pref field.",
            )
        parser.add_argument(
            '-w', '--weight',
            action='store',
            default=1,
            type=int,
            help="Used when more than one service has the same priority. A 16 bit unsigned integer in the range 0 - 65535. The value 0 indicates no weighting should be applied. If the weight is 1 or greater it is a relative number in which the highest is most frequently delivered, that is, given two SRV records both with Priority = 0, one with weight = 1 the other weight = 6, the one with weight 6 will have its RR delivered first 6 times out of 7 by the name server.",
            )
        parser.add_argument(
            'domain',
            action='store',
            default=None,
            help="Domain name for the record",
            )
        parser.add_argument(
            'service',
            action='store',
            help="""Defines the symbolic service name (see IANA port-numbers) prepended with a '_' (underscore). Case insensitive. Common values are:
_http - web service
_ftp - file transfer service
_ldap - LDAP service
_imap - IMAP mail service
_PKIXREP - PKIX Repository (X.509 certificates) """,
            )
        parser.add_argument(
            'protocol',
            action='store',
            default=None,
            help="""Defines the protocol name (see IANA service-names) prepended with a '_' (underscore). Case insensitive. Common values are
_tcp - TCP protocol
_udp - UDP protocol""",
            )
        parser.add_argument(
            'port',
            action='store',
            help="Normally the port number assigned to the symbolic service but this is not a requirement, for instance, it is permissible to define a _http service with a port number of 8100 rather than the more normal port 80.",
            )
        parser.add_argument(
            'target',
            action='store',
            default=None,
            help="The name of the host that will provide this service. Does not have to be in the same zone (domain). May be just a host name or a FQDN.",
            )

    def handle(self, *args, **options):
        if options['domain'] == None:
            raise CommandError("Need a Domain Name.")
        else:
            domainname = options['domain']
        if options['target'] == None:
            raise CommandError("Need a host target.")
        if options['port'] == None:
            raise CommandError("Need a port number for the service.")

        if options['service'] != None:
            if options['protocol'] != None:
                name = f"{options['service']}.{options['protocol']}"
            else:
                name = options['service']
        else:
            if options['protocol'] != None:
                name = options['protocol']
            else:
                raise CommandError("Need a service or protocol.")

        searchname = name + "." + domainname

        try:
            domain = Domain.objects.get(name__icontains=domainname)
        except:
            raise CommandError('Domain not found. Exiting')

        srv_record = SRV_Record.objects.create(
            domain=domain,searchdomain=domain.name,
            name=name,
            searchname=searchname,
            ttl=options['ttl'],
            priority=options['priority'],
            weight=options['weight'],
            port=options['port'],
            target=options['target'],
            source=SOURCE_SCRIPT,
            )
        srv_record.save()
        print(f'Created SRV Record {srv_record} under domain {domain}.')




