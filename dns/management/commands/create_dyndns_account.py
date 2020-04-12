"""
Create Dynamic DNS account
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings

from dns.models import Domain, DynamicDNSAccount

class Command(BaseCommand):
    help = ('Create a Dynamic DNS account with username as its owner')

    def add_arguments(self, parser):
        parser.add_argument(
            '-u','--username',
            action='store',
            default=None,
            help='Local owner of Dynamic DNS account. Otherwise will use first user',
            )
        parser.add_argument(
            '-p','--password',
            action='store',
            default=None,
            help='Default password for Dynamic DNS account',
            )
        parser.add_argument(
            'accountname',
            nargs='?',
            action='store',
            default=None,
            help="Dynamic DNS account name",
            )
        parser.add_argument(
            'domains',
            nargs='*',
            action='store',
            default=None,
            help='Dynamic DNS domains for account',
            )

    def handle(self, *args, **options):
        if options['accountname'] == None:
            raise CommandError("Need a Dynamic DNS Account Name.")
        if options['username'] == None:
            user = User.objects.all()[0]
            print(f'Using default user: {user}')
        else:
            user = User.objects.get(username=options['username'])
        domains = Domain.objects.filter(name__in=options['domains'])
        dyndns, created = DynamicDNSAccount.objects.get_or_create(
            owner=user,
            username=options['accountname'])
        dyndns.password = options['password']
        dyndns.domains.clear()
        dyndns.domains.add(*domains)
        dyndns.save()
        domains_list = ", ".join(str(domain) for domain in domains)
        if created:
            print(f'Created Dynamic DNS account {dyndns} with domains {domains_list}.')
        else:
            print(f'Updated Dynamic DNS account {dyndns} with domains {domains_list}.')
