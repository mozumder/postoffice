"""
Create Domain
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings

from dns.models import Domain, SOA_Record, NS_Record, SOURCE_SCRIPT

class Command(BaseCommand):
    help = ("Create a zone with username as its owner")

    def add_arguments(self, parser):
        parser.add_argument(
            '-u','--username',
            action='store',
            default=None,
            help="Username of domain owner. Otherwise will use first user",
            )
        parser.add_argument(
            '-e','--email',
            action='store',
            default=None,
            help="Email address of the person responsible for this domain and to which email may be sent to report errors or problems. If not set, will use email address of user. This is RNAME in the domain's SOA record.",
            )
        parser.add_argument(
            '-ttl',
            action='store',
            default=settings.RECORD_TTL,
            type=int,
            help="Default time-to-live in seconds. Slave DNS do not use this value.",
            )
        parser.add_argument(
            '-ref','--refresh',
            action='store',
            default=43200,
            type=int,
            help="SOA record REFRESH field time in seconds. Indicates the time when the slave will try to refresh the zone from the master (by reading the master DNS SOA RR). RFC 1912 recommends 1200 to 43200 seconds, low (1200) if the data is volatile or 43200 (12 hours) if it's not. If you are using NOTIFY you can set it to much higher values, for instance, 1 or more days (> 86400 seconds).",
            )
        parser.add_argument(
            '-ret','--retry',
            action='store',
            default=3600,
            type=int,
            help="SOA record RETRY field time in seconds between retries if the slave (secondary) fails to contact the master when refresh (above) has expired or a NOTIFY message is received. Typical values would be 180 (3 minutes) to 900 (15 minutes) or higher.",
            )
        parser.add_argument(
            '-ex','--expiry',
            action='store',
            default=2419200 ,
            type=int,
            help="SOA record EXPIRE field time in seconds when the zone data is no longer authoritative. Used by Slave (Secondary) servers only. BIND9 slaves stop responding authoritatively to queries for the zone when this time has expired and no contact has been made with the master. Thus, every time the refresh values expires (or a NOTIFY message is received) the slave will attempt to read the SOA record from the zone master - and initiate a zone transfer AXFR/IXFR if sn is HIGHER. If contact is made the expiry and refresh values are reset and the cycle starts again. If the slave fails to contact the master it will retry every retry period but continue to respond authoritatively for the zone until the expiry value is reached at which point it will stop answering authoritatively for the domain. RFC 1912 recommends 1209600 to 2419200 seconds (2-4 weeks) to allow for major outages of the zone master.",
            )
        parser.add_argument(
            '-nx','--nxdomain',
            action='store',
            default=180 ,
            type=int,
            help="SOA record NX field time in seconds redefined by RFC 2308 to be the negative caching time - the time a NAME ERROR = NXDOMAIN result may be cached by any resolver. The maximum value allowed by RFC 2308 for this parameter is 3 hours (10800 seconds). Note: This value was historically (in BIND 4 and 8) used to hold the default TTL value for any RR from the zone that did not specify an explicit TTL. RFC 2308 (and BIND 9) uses the $TTL directive as the zone default TTL. You may find older documentation or zone file configurations which reflect the old usage",
            )
        parser.add_argument(
            'name',
            action='store',
            default=None,
            help="Zone to be created. This is MNAME of the domain's SOA record.",
            )
        parser.add_argument(
            'name_server',
            action='store',
            nargs='+',
            default=None,
            help="List of name servers that will respond authoritatively for the domain. . First nameserver will be primary domain.",
            )

    def handle(self, *args, **options):
#        print(options)
        if options['name'] == None:
            raise CommandError("Need a Domain Name.")
        else:
            domainname = options['name']
        if options['name_server'] == None:
            raise CommandError("Need a Name Server.")
        if options['username'] == None:
            user = User.objects.all()[0]
            print(f'Using default user: {user}')
        else:
            user = User.objects.get(username=options['username'])
        if options['email'] == None:
            email = user.email
            print(f'Using default user email: {email}')
        else:
            email = options['email']

        d, d_created = Domain.objects.get_or_create(owner=user,name=domainname)
        d.save()
        if d_created:
            print(f'Created domain {d} with owner {d.owner}.')
        else:
            print(f'Domain {d} with owner {d.owner} already exists.')

        soa_record, soa_created = SOA_Record.objects.get_or_create(domain=d,searchdomain=d.name)
        soa_record.host = None
        soa_record.ttl = options['ttl']
        soa_record.rname = email
        soa_record.mname = options['name']
        soa_record.nameserver = options['name_server'][0]
        soa_record.refresh = options['refresh']
        soa_record.retry = options['retry']
        soa_record.serial = 0
        soa_record.expiry = options['expiry']
        soa_record.nx = options['nxdomain']
        soa_record.source = SOURCE_SCRIPT
        soa_record.save()
        if soa_created:
            print(f'Created SOA Record {soa_record} under domain {d}.')
        else:
            print(f'SOA Record {soa_record} under domain {d} updated.')

        for ns in options['name_server']:
            ns_record, ns_created = NS_Record.objects.get_or_create(domain=d,searchdomain=d.name,name=ns)
            ns_record.ttl = options['ttl']
            ns_record.searchname = domainname
            ns_record.source = SOURCE_SCRIPT
            ns_record.save()
            if ns_created:
                print(f'Created NS Record {ns_record} under domain {d}.')
            else:
                print(f'NS Record {ns_record} under domain {d} updated.')

