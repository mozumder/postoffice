# The files in this directory are from the Django-Vmail package: https://github.com/lgunsch/django-vmail/tree/master/vmail
# These are included here per license given under MIT License for that package.

"""
Add an email alias entry command.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from accounts.models import Domain, Alias

HELP_TEXT = """
This will create an email aliases, forwarding address, or
catch-all alias (@example.com) by adding an Alias entry
with the given source and destination addresses.
Neither the souce address, nor the destination address is
required to be an existing MailUser. If --create-domain
is used then the domain is also created if it does not exist.
A virtual alias cannot receive mail, but may only forward
mail to other email addresses.  The source address may be
repeated for each destination mailbox to forward to, and
may also forward to a mailbox of the same address to keep
a copy of an email.  A source address may also be missing
the name portion if the destination address is to be a
catch-all mailbox.  Source and destination addresses are
not required to be local, and thus are not necessarily
related to local virtual mailbox users.
        @example.org  >  john@example.org  # catch-all alias
    john@example.org  >  john@example.org  # keep a copy in local mailbox
    john@example.org  >  jeff@example.com  # forward john to jeff
"""


class Command(BaseCommand):
    args = 'owner-domain source-address destination-address [--create-domain]'
    help = (HELP_TEXT)
    def add_arguments(self, parser):
        parser.add_argument('domain',
            help='Owner domain')
        parser.add_argument('source',
            help='Virtual email address')
        parser.add_argument('destination',
            help='Destination email address')
        parser.add_argument('--create-domain',
                    action='store_true',
                    dest='create_domain',
                    default=False,
                    help='Create the domain which will own the alias if it does not already exist.'),

    def handle(self, *args, **options):
        usage = 'Required arguments: owner-domain source-address destination-address [--create-domain]'
        try:
            fqdn = options['domain'].strip().lower()
        except:
            raise CommandError(usage)

        try:
            source = options['source'].strip().lower()
        except:
            raise CommandError(usage)


        if fqdn.startswith('@'):
            fqdn = fqdn[1:]

        try:
            destination = options['destination'].strip().lower()
        except:
            raise CommandError(usage)

        try:
            validate_email(destination)
        except ValidationError:
            msg = 'Improperly formatted email address: {0}.'.format(destination)
            raise CommandError(msg)

        try:
            domain = Domain.objects.get(fqdn=fqdn)
        except Domain.DoesNotExist:
            if options['create_domain']:
                domain = Domain.objects.create(fqdn=fqdn)
                self.stdout.write('Created domain: {0}.\n'.format(str(domain)))
            else:
                raise CommandError("Domain '{0}', does not exist.".format(fqdn))

        try:
            Alias.objects.create(domain=domain, source=source,
                                 destination=destination)
        except IntegrityError:
            raise CommandError('Alias exists already.')

        self.stdout.write('Success.\n')

