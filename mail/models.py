from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.

class Mailbox(models.Model):
    """Represents a users's real mailbox."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    name = models.CharField(
        _('Name'),
        max_length=256)
    parent = models.ForeignKey(
        'Mailbox',
        on_delete=models.CASCADE,)

class Message(models.Model):
    """Represents the actual mail message."""
    mailbox = models.ForeignKey(
        'Mailbox',
        on_delete=models.CASCADE,)
    date = models.DateTimeField(
        verbose_name=_('Date'),)
    from_address = models.CharField(
        _('From'),
        max_length=256)
    to_address = models.CharField(
        _('To'),
        max_length=4096)
    cc = models.CharField(
        _('CC'),
        max_length=4096,
        null=True, blank=True)
    bcc = models.CharField(
        _('BCC'),
        max_length=4096,
        null=True, blank=True)
    subject = models.CharField(
        _('Subject'),
        max_length=256)
    body = models.TextField(
        _('Body'),)


class Envelope(models.Model):
    """Represents the publicly visible to/from."""
    msg = models.OneToOneField(
        'Message',
        on_delete=models.CASCADE)
    message_id = models.CharField(
        _('Message-ID'),
        max_length=256)
    sender = models.CharField(
        _('Sender'),
        max_length=256)
    receiver = models.CharField(
        _('Receiver'),
        max_length=4096)
