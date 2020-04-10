from django.db import models

# Create your models here.


class FileRule(models.Model):
    """
    Messages that containts matching header fields get filed into folders
    """
    mailbox = models.ForeignKey('accounts.MailUser',on_delete=models.CASCADE, help_text='From:')
    field = models.CharField(max_length=100, help_text='From:')
    contains = models.CharField(max_length=100, help_text='From:')
    folder = models.CharField(max_length=150, help_text='Folder to file into')

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.field}: {self.contains} -> {self.folder}"

    def rule_create(self):
        return f"""if header :contains "{self.field}" "{self.contains}" {fileinto :create "{self.folder}"; return;}"""

    class Meta:
        unique_together = [['mailbox','field','contains','folder']]
        ordering = ['mailbox', 'folder', 'contains', 'field']
