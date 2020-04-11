"""
Continously ping a target site and update DNS if current IP address changes.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
#    args = 'mailbox rulesfile'
    help = ('Continously ping a target site and update DNS if current IP address changes..')

    def add_arguments(self, parser):
        parser.add_argument('--target',
                    action='store_true',
                    dest='target',
                    default=settings.PING_TARGET,
                    help='Target website to ping that responds with your IP address')
        parser.add_argument('--interval',
                    action='store_true',
                    dest='interval',
                    default=600,
                    help='Ping interval in seconds.')

    def handle(self, *args, **options):
#        usage = 'Required arguments: mailbox rulesfile'

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


