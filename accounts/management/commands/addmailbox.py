# The files in this directory are from the Django-Vmail package: https://github.com/lgunsch/django-vmail/tree/master/vmail
# These are included here per license given under MIT License for that package.

"""
Set password command for administrators to set the password of existing
mail users.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from accounts.models import MailUser, Domain


class Command(BaseCommand):
    args = 'email [--create-domain] [--password password]'
    help = ('Create a new MailUser account, with no set password. If\n'
            '--create-domain is used then the domain is also created,\n'
            'given it does not exist. If --password is used then the\n'
            'password is set.')

    def add_arguments(self, parser):
        parser.add_argument('email',
                    help='Email address to add')
        parser.add_argument('--create-domain',
                    action='store_true',
                    dest='create_domain',
                    default=False,
                    help='Create the domain if it does not already exist.')
        parser.add_argument('--password',
                    dest='password',
                    default=None,
                    help='Set the default password for the user.')

    def handle(self, *args, **options):
        usage = 'Required arguments: email [--create-domain] [--password password]'
        try:
            email = options['email'].strip().lower()
        except:
            raise CommandError(usage)
        try:
            validate_email(email)
        except ValidationError:
            raise CommandError('Improperly formatted email address.')

        username, fqdn = email.split('@')
        username = username.strip()

        try:
            MailUser.objects.get(username=username, domain__fqdn=fqdn)
        except MailUser.DoesNotExist:
            pass
        else:
            raise CommandError('Username exist already.')

        try:
            domain = Domain.objects.get(fqdn=fqdn)
        except Domain.DoesNotExist:
            if options['create_domain']:
                domain = Domain.objects.create(fqdn=fqdn)
                self.stdout.write('Created domain: {0}.\n'.format(str(domain)))
            else:
                raise CommandError('Domain does not exist.')

        user = MailUser.objects.create(username=username, domain=domain)
        if options['password'] is not None:
            user.set_password(options['password'])
            user.save()
            self.stdout.write('Set the password.\n')

        self.stdout.write('Success.\n')

