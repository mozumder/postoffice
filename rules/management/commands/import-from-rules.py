"""
Set password command for administrators to set the password of existing
mail users.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

import csv

from accounts.models import Domain, MailUser
from rules.models import FileRule

class Command(BaseCommand):
    args = 'mailbox rulesfile'
    help = ('reads a CSV file with From-emails and Folder to file them into for specified mailbox.')

    def add_arguments(self, parser):
        parser.add_argument('mailbox',
                    help='User mailbox to add rules')
        parser.add_argument('rulesfile',
                    help='CSV file of "Field, Contains, Folder" rules')
        parser.add_argument('--reset',
                    action='store_true',
                    dest='reset',
                    default=False,
                    help='Erase all previously created rules and create new rules database.')


    def handle(self, *args, **options):
        usage = 'Required arguments: mailbox rulesfile'

        try:
            mailbox = options['mailbox'].strip().lower()
        except:
            raise CommandError(usage)

        try:
            rulesfilename = options['rulesfile'].strip()
        except:
            raise CommandError(usage)

        try:
            user = MailUser.get_from_email(mailbox)
        except ValidationError:
            raise CommandError('Improperly formatted email address.')
        except Domain.DoesNotExist:
            raise CommandError('Domain does not exist.')
        except MailUser.DoesNotExist:
            raise CommandError('Username does not exist.')

        if options['reset'] == True:
            self.stdout.write('Erasing previous rules!!!')
            count = 0
            rules = FileRule.objects.filter(mailbox=user)
            for rule in rules:
                rule.delete()
                count = count + 1
            self.stdout.write(f'  - Erased {count} rules')

        self.stdout.write(f'Adding rules for mailbox: {user}')

        with open(rulesfilename) as rulesfile:
            readCSV = csv.reader(rulesfile, delimiter=',', skipinitialspace=True)
            for row in readCSV:
            #
            # Need to strip out dangerous characters
            #
                field = row[0].strip().replace("'", '').replace('"', '').replace('\\', '')
                contains = row[1].strip().replace("'", '').replace('"', '').replace('\\', '')
                # SECURITY TODO: Strip Single quotes (but they are needed).
                folder = row[2].strip().replace('"', '').replace('\\', '')
                rule = FileRule(mailbox=user, field=field,contains=contains,folder=folder)
                rule.save()
                self.stdout.write(f"Added rule: {field}: {contains} -> {folder}")

        self.stdout.write('Success.\n')

