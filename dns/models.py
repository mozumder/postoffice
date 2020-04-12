from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Domain(models.Model):
    owner = models.ForeignKey(
        User,
        verbose_name="Owner",
        related_name="domain_owner",
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name='Domain Name',
        max_length=80)
    date_updated = models.DateTimeField(
        auto_now=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Domain Name'
        indexes = [
            models.Index(
                fields = [
                    'owner',
                    'name'],
                name='domain_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'owner',
                    'name'],
                name='domain_uniques')
        ]

class Host(models.Model):
    name = models.CharField(
        verbose_name='Host',
        max_length=120)
    domain = models.ForeignKey(
        Domain,
        verbose_name="Domain",
        on_delete=models.CASCADE)
    date_updated = models.DateTimeField(
        auto_now=True)
    def host_name(self):
        return self.name
    def __str__(self):
        return f'{self.name}.{self.domain.name}'
    def domain_name(self):
        names = self.name.split(".")[1:]
        tld = names[-1]
        if len(names) > 1:
            domain = names[-2] + '.' + tld
        else:
            domain = ''
        if len(names) > 2:
            domain = names[-3] + "." + domain
        return domain
    class Meta:
        verbose_name = 'Host Name'
        indexes = [
            models.Index(
                fields = [
                    'name',
                    'domain'],
                name='host_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'name',
                    'domain'],
                name='host_uniques')
        ]

class A_Record(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=120,
        null=True, blank=True)
    ip_address = models.GenericIPAddressField(
        verbose_name='IP Address',
        db_index=True)
    domain = models.ForeignKey(
        Domain,
        verbose_name="Domain",
        on_delete=models.CASCADE)
    host = models.ForeignKey(
        Host,
        verbose_name="Host",
        null=True, blank=True,
        on_delete=models.CASCADE)
    ttl = models.IntegerField(
        verbose_name="TTL",
        default=settings.RECORD_TTL)
    dynamic_ip = models.BooleanField(
        verbose_name="Dynamic IP",
        default=False)
    date_updated = models.DateTimeField(
        auto_now=True)
    def __str__(self):
        if self.host:
            return f'{self.name}.{self.domain.name}'
        else:
            return f'.{self.domain.name}'
    def domain_name(self):
        names = self.name.split(".")[1:]
        tld = names[-1]
        if len(names) > 1:
            domain = names[-2] + '.' + tld
        else:
            domain = ''
        if len(names) > 2:
            domain = names[-3] + "." + domain
        return domain
    class Meta:
        ordering = ['domain','name']
        verbose_name = 'A Record'
        indexes = [
            models.Index(
                fields = [
                    'name',
                    'domain'],
                name='a_record_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'name',
                    'domain'],
                name='a_record_uniques'),
        ]

class DynamicDNSAccount(models.Model):
    owner = models.ForeignKey(
        User,
        verbose_name="Owner",
        related_name="dyndnsaccount_owner",
        on_delete=models.CASCADE)
    domains = models.ManyToManyField(Domain)
    username = models.CharField(
        verbose_name='User Name',
        max_length=15)
    password = models.CharField(
        verbose_name='Password',
        max_length=40,
        null=True, blank=True)
    date_updated = models.DateTimeField(
        auto_now=True)
    def __str__(self):
        return self.username
    class Meta:
        verbose_name = 'Dynamic DNS Account'
        indexes = [
            models.Index(
                fields = [
                    'owner',
                    'username'],
                name='dyndnsaccount_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'owner',
                    'username'],
                name='dyndnsaccount_uniques')
        ]


class DynamicDNS(models.Model):
    a_record = models.OneToOneField(
        A_Record,
        on_delete=models.CASCADE)
    dyndns_id = models.CharField(
        verbose_name='Record ID',
        max_length=15,
        db_index=True, unique=True)
    password = models.CharField(
        verbose_name='Record Password',
        max_length=40,
        null=True, blank=True)
    date_updated = models.DateTimeField(
        auto_now=True)

    def __str__(self):
        return f'{self.a_record}:{self.dyndns_id}'

    class Meta:
        verbose_name = 'Dynamic DNS Record'


class IPLog(models.Model):
    address = models.GenericIPAddressField(
        verbose_name='IP Address',
        db_index=True)
    date_updated = models.DateTimeField(
        default=timezone.now,
        db_index=True)

    def __str__(self):
        return self.address

    class Meta:
        ordering = ['-date_updated']
        verbose_name = 'IP Address'
        verbose_name_plural = 'IP Addresses'
