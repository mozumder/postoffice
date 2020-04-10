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

        self.stdout.write(f'Creating sieve file for mailbox: {user}')
        
        username = user.username
        fqdn = user.domain.fqdn

        rules = FileRule.objects.filter(mailbox__username__exact=username, mailbox__domain__fqdn__exact=fqdn)
        
        command = f"sieve-filter -e -W -v -C -u {mailbox} {rulesfilename} 'INBOX'"

        with open(rulesfilename, "w+") as sieveFile:
            sieveFile.write(f"""# To run:
#   % su vmail
#   % cp {rulesfilename} /var/vmail/home/{fqdn}/{username}/sieve/file.sieve
#   % sievec /var/vmail/home/{fqdn}/{username}/sieve/file.sieve
#   % chmod 700 /var/vmail/home/{fqdn}/{username}/sieve/file.sieve
#   # chmod 600 /var/vmail/home/{fqdn}/{username}/sieve/file.svbin
#   % chown vmail:vmail /var/vmail/home/{fqdn}/{username}/sieve/file.*
#   % {command}
""")
            sieveFile.write('require ["fileinto","mailbox","include","regex","copy"];\n')
            for rule in rules:
                sieveFile.write(f'if header :contains "{rule.field}" "{rule.contains}" {{fileinto :create "{rule.folder}";return;}}\n')
                self.stdout.write(f"Wrote rule: {rule.field}: {rule.contains} -> {rule.folder}")

        
        self.stdout.write('Success.\n')
        self.stdout.write(f"""To run:
 
 su vmail
 cp {rulesfilename} /var/vmail/home/{fqdn}/{username}/sieve/file.sieve
 sievec /var/vmail/home/{fqdn}/{username}/sieve/file.sieve
 chmod 700 /var/vmail/home/{fqdn}/{username}/sieve/file.sieve
 chmod 600 /var/vmail/home/{fqdn}/{username}/sieve/file.svbin
 chown vmail:vmail /var/vmail/home/{fqdn}/{username}/sieve/file.*
 {command}""")

