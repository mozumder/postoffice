from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

SOURCE_ADMIN = '0'
SOURCE_SCRIPT = '1'
SOURCE_WEB = '2'
SOURCE_API = '3'
SOURCE_CHOICES = (
    (SOURCE_ADMIN, 'Admin'),
    (SOURCE_SCRIPT, 'Script'),
    (SOURCE_WEB, 'Web'),
    (SOURCE_API, 'API'),
    (SOURCE_API, 'Socket'),
)
SOURCE_LOOKUP_DICT = dict(tuple((i[1].lower(),i[0]) for i in SOURCE_CHOICES))

# Create your models here.

class Domain(models.Model):
    owner = models.ForeignKey(
        User,
        verbose_name=_("Owner"),
        related_name="domain_owner",
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_("Domain Name"),
        max_length=255)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = _("Domain")
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
        verbose_name=_("Name"),
        max_length=64)
    domain = models.ForeignKey(
        Domain,
        verbose_name=_("Domain"),
        on_delete=models.CASCADE)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
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
        verbose_name = _("Host")
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

class DynamicDNSAccount(models.Model):
    owner = models.ForeignKey(
        User,
        verbose_name=_("Owner"),
        related_name="dyndnsaccount_owner",
        on_delete=models.CASCADE)
    domains = models.ManyToManyField(Domain)
    username = models.CharField(
        verbose_name=_("User Name"),
        max_length=15)
    password = models.CharField(
        verbose_name=_("Password"),
        max_length=40,
        null=True, blank=True)
    endpoint = models.URLField(
        verbose_name=_("DNS Update Endpoint URL"),
        max_length=150)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)
    def __str__(self):
        return self.username
    class Meta:
        verbose_name = _("Dynamic DNS Account")
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
        'A_Record',
        on_delete=models.CASCADE)
    dyndns_id = models.CharField(
        verbose_name=_("Record ID"),
        max_length=15,
        db_index=True, unique=True)
    password = models.CharField(
        verbose_name=_("Record Password"),
        max_length=40,
        null=True, blank=True)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)

    def __str__(self):
        return f'{self.a_record}:{self.dyndns_id}'

    class Meta:
        verbose_name = 'Dynamic DNS Record'

class IPLog(models.Model):
    ip = models.GenericIPAddressField(
        verbose_name=_("IP Address"),
        db_index=True)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        default=timezone.now,
        db_index=True)

    def __str__(self):
        return self.ip

    class Meta:
        ordering = ['-date_updated']
        verbose_name = 'IP Address'
        verbose_name_plural = 'IP Addresses'

class SOA_Record(models.Model):
    domain = models.ForeignKey(
        Domain,
        verbose_name=_("Domain"),
        on_delete=models.CASCADE)
    origin = models.CharField(
        verbose_name=_("Origin"),
        max_length=255,
        null=True, blank=True)
    rname = models.CharField(
        verbose_name=_("Responsible Party Name"),
        max_length=255,
        null=True, blank=True)
    nameserver = models.CharField(
        verbose_name=_("Name Server"),
        max_length=255,
        null=True, blank=True)
    nameserver_host = models.ForeignKey(
        Host,
        verbose_name=_("Name Server Host"),
        null=True, blank=True,
        on_delete=models.CASCADE)
    refresh = models.IntegerField(
        verbose_name=_("Refresh Time"),
        default=43200)
    retry = models.IntegerField(
        verbose_name=_("Retry Time"),
        default=3600)
    expiry = models.IntegerField(
        verbose_name=_("Expiration Time"),
        default=1209600)
    nxttl = models.IntegerField(
        verbose_name=_("Negative Caching Time"),
        default=180)
    ttl = models.IntegerField(
        verbose_name=_("Time-to-Live"),
        default=settings.RECORD_TTL)
    serial = models.IntegerField(
        verbose_name=_("Serial Number"),
        default=0)
    source = models.CharField(
        _("Source"),
        max_length=1,
        choices=SOURCE_CHOICES,
        default=SOURCE_ADMIN)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)
    def __str__(self):
        return f'{self.origin}'
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
        ordering = ['domain']
        verbose_name = 'SOA Record'
        indexes = [
            models.Index(
                fields = [
                    'domain'],
                name='soa_record_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'domain'],
                name='soa_record_uniques'),
        ]

class A_Record(models.Model):
    domain = models.ForeignKey(
        Domain,
        verbose_name=_("Domain"),
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=64,
        null=True, blank=True)
    searchname = models.CharField(
        verbose_name=_("Fully Qualified Domain Name"),
        max_length=255,
        null=True, blank=True)
    ip_address = models.GenericIPAddressField(
        verbose_name=_("IP Address"),
        protocol='IPv4',
        db_index=True)
    host = models.ForeignKey(
        Host,
        verbose_name=_("Host"),
        null=True, blank=True,
        on_delete=models.CASCADE)
    roundrobin = models.BooleanField(
        verbose_name=_("Next Round Robin"),
        default=False)
    dynamic_ip = models.BooleanField(
        verbose_name=_("Dynamic IP"),
        default=False)
    ttl = models.IntegerField(
        verbose_name=_("Time-to-Live"),
        default=settings.RECORD_TTL)
    serial = models.IntegerField(
        verbose_name=_("Serial Number"),
        default=0)
    source = models.CharField(
        _("Source"),
        max_length=1,
        choices=SOURCE_CHOICES,
        default=SOURCE_ADMIN)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)
    def __str__(self):
        if self.host:
            return f'{self.name}.{self.domain.name}:{self.ip_address}'
        else:
            return f'.{self.domain.name}:{self.ip_address}'
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

class AAAA_Record(models.Model):
    domain = models.ForeignKey(
        Domain,
        verbose_name=_("Domain"),
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=64,
        null=True, blank=True)
    searchname = models.CharField(
        verbose_name=_("Fully Qualified Domain Name"),
        max_length=255,
        null=True, blank=True)
    ip_address = models.GenericIPAddressField(
        verbose_name=_("IP Address"),
        protocol='IPv6',
        db_index=True)
    host = models.ForeignKey(
        Host,
        verbose_name=_("Host"),
        null=True, blank=True,
        on_delete=models.CASCADE)
    ttl = models.IntegerField(
        verbose_name=_("Time-to-Live"),
        default=settings.RECORD_TTL)
    serial = models.IntegerField(
        verbose_name=_("Serial Number"),
        default=0)
    source = models.CharField(
        _("Source"),
        max_length=1,
        choices=SOURCE_CHOICES,
        default=SOURCE_ADMIN)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)
    def __str__(self):
        if self.host:
            return f'{self.name}.{self.domain.name}:{self.ip_address}'
        else:
            return f'.{self.domain.name}:{self.ip_address}'
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
        verbose_name = 'AAAA Record'
        indexes = [
            models.Index(
                fields = [
                    'name',
                    'domain'],
                name='aaaa_record_idx'),
        ]

class CNAME_Record(models.Model):
    domain = models.ForeignKey(
        Domain,
        verbose_name=_("Domain"),
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_("Alias Name"),
        max_length=64)
    searchname = models.CharField(
        verbose_name=_("Fully Qualified Domain Name"),
        max_length=255,
        null=True, blank=True)
    canonical_name = models.CharField(
        #If the value ends in a dot, it is for an external domain.
        verbose_name=_("Canonical Name"),
        max_length=255)
    host = models.ForeignKey(
        Host,
        verbose_name=_("Canonical Host"),
        null=True, blank=True,
        on_delete=models.CASCADE)
    ttl = models.IntegerField(
        verbose_name=_("Time-to-Live"),
        default=settings.RECORD_TTL)
    serial = models.IntegerField(
        verbose_name=_("Serial Number"),
        default=0)
    source = models.CharField(
        _("Source"),
        max_length=1,
        choices=SOURCE_CHOICES,
        default=SOURCE_ADMIN)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)
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
        ordering = ['domain','name']
        verbose_name = _("CNAME Record")
        indexes = [
            models.Index(
                fields = [
                    'name',
                    'domain'],
                name='cname_record_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'name',
                    'domain'],
                name='cname_record_uniques'),
        ]

class MX_Record(models.Model):
    domain = models.ForeignKey(
        Domain,
        verbose_name=_("Domain"),
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=64,
        null=True, blank=True)
    searchname = models.CharField(
        verbose_name=_("Fully Qualified Domain Name"),
        max_length=255,
        null=True, blank=True)
    hostname = models.CharField(
        #If the value ends in a dot, it is for an outside domain.
        verbose_name=_("Hostname"),
        max_length=64,
        null=True, blank=True)
    host = models.ForeignKey(
        Host,
        verbose_name=_("Mail Server Host"),
        null=True, blank=True,
        on_delete=models.CASCADE)
    preference = models.IntegerField(
        verbose_name=_("Preference"),
        default=0)
    ttl = models.IntegerField(
        verbose_name=_("Time-to-Live"),
        default=settings.RECORD_TTL)
    serial = models.IntegerField(
        verbose_name=_("Serial Number"),
        default=0)
    source = models.CharField(
        _("Source"),
        max_length=1,
        choices=SOURCE_CHOICES,
        default=SOURCE_ADMIN)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)
    def __str__(self):
        if self.name:
            return f'{self.name}.{self.domain.name}'
        else:
            return f'{self.domain.name}'
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
        verbose_name = _("MX Record")
        indexes = [
            models.Index(
                fields = [
                    'name',
                    'domain'],
                name='mx_record_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'name',
                    'domain'],
                name='mx_record_uniques'),
        ]

class TXT_Record(models.Model):
    domain = models.ForeignKey(
        Domain,
        verbose_name=_("Domain"),
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=64,
        null=True, blank=True)
    searchname = models.CharField(
        verbose_name=_("Fully Qualified Domain Name"),
        max_length=255,
        null=True, blank=True)
    value = models.CharField(
        verbose_name=_("Value"),
        max_length=65535,
        null=True, blank=True)
    ttl = models.IntegerField(
        verbose_name=_("Time-to-Live"),
        default=settings.RECORD_TTL)
    serial = models.IntegerField(
        verbose_name=_("Serial Number"),
        default=0)
    source = models.CharField(
        _("Source"),
        max_length=1,
        choices=SOURCE_CHOICES,
        default=SOURCE_ADMIN)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)
    def __str__(self):
        return f'{self.name}: {self.value}'
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
        verbose_name = _("TXT Record")
        indexes = [
            models.Index(
                fields = [
                    'domain'],
                name='txt_record_idx'),
        ]

class PTR_Record(models.Model):
    domain = models.ForeignKey(
        Domain,
        verbose_name=_("Domain"),
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=64)
    searchname = models.CharField(
        verbose_name=_("Fully Qualified Domain Name"),
        max_length=255,
        null=True, blank=True)
    hostname = models.CharField(
        #If the value ends in a dot, it is for an external domain.
        verbose_name=_("Host Name"),
        max_length=64)
    host = models.ForeignKey(
        Host,
        verbose_name=_("Host"),
        null=True, blank=True,
        on_delete=models.CASCADE)
    ttl = models.IntegerField(
        verbose_name=_("Time-to-Live"),
        default=settings.RECORD_TTL)
    serial = models.IntegerField(
        verbose_name=_("Serial Number"),
        default=0)
    source = models.CharField(
        _("Source"),
        max_length=1,
        choices=SOURCE_CHOICES,
        default=SOURCE_ADMIN)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)
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
        ordering = ['domain','name']
        verbose_name = _("PTR Record")
        indexes = [
            models.Index(
                fields = [
                    'name',
                    'domain'],
                name='ptr_record_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'name',
                    'domain'],
                name='ptr_record_uniques'),
        ]

class NS_Record(models.Model):
    domain = models.ForeignKey(
        Domain,
        verbose_name=_("Domain"),
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=64)
    searchname = models.CharField(
        verbose_name=_("Fully Qualified Domain Name"),
        max_length=255,
        null=True, blank=True)
    delegate = models.CharField(
        #If the value ends in a dot, it is for an external domain.
        verbose_name=_("Delegate"),
        max_length=64)
    delegate_host = models.ForeignKey(
        Host,
        verbose_name=_("Delegate Host"),
        null=True, blank=True,
        on_delete=models.CASCADE)
    ttl = models.IntegerField(
        verbose_name=_("Time-to-Live"),
        default=settings.RECORD_TTL)
    serial = models.IntegerField(
        verbose_name=_("Serial Number"),
        default=0)
    source = models.CharField(
        _("Source"),
        max_length=1,
        choices=SOURCE_CHOICES,
        default=SOURCE_ADMIN)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)
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
        ordering = ['domain','name']
        verbose_name = _("NS Record")
        indexes = [
            models.Index(
                fields = [
                    'name',
                    'domain'],
                name='ns_record_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'name',
                    'domain'],
                name='ns_record_uniques'),
        ]

class SRV_Record(models.Model):
    domain = models.ForeignKey(
        Domain,
        verbose_name=_("Domain"),
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=64,
        null=True, blank=True)
    searchname = models.CharField(
        verbose_name=_("Search Name"),
        max_length=255,
        null=True, blank=True)
    priority = models.IntegerField(
        verbose_name=_("Priority"))
    weight = models.IntegerField(
        verbose_name=_("Weight"))
    port = models.IntegerField(
        verbose_name=_("Port"))
    target = models.CharField(
        verbose_name=_("Target"),
        max_length=64,
        null=True, blank=True)
    host = models.ForeignKey(
        Host,
        verbose_name=_("Host"),
        null=True, blank=True,
        on_delete=models.CASCADE)
    ttl = models.IntegerField(
        verbose_name="TTL",
        default=settings.RECORD_TTL)
    serial = models.IntegerField(
        verbose_name=_("Serial Number"),
        default=0)
    source = models.CharField(
        _("Source"),
        max_length=1,
        choices=SOURCE_CHOICES,
        default=SOURCE_ADMIN)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)
    def __str__(self):
        return f'{self.name}: {self.target}'
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
        verbose_name = _("SRV Record")
        indexes = [
            models.Index(
                fields = [
                    'name',
                    'domain'],
                name='SRV_record_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'name',
                    'domain'],
                name='SRV_record_uniques'),
        ]

CAA_TYPE_ISSUE = 0
CAA_TYPE_ISSUEWILD = 1
CAA_TYPE_IODEF = 2
CAA_TYPE_CHOICES = (
    (CAA_TYPE_ISSUE, 'issue'),
    (CAA_TYPE_ISSUEWILD, 'issuewild'),
    (CAA_TYPE_IODEF, 'iodef'),
)
CAA_TYPE_LOOKUP_DICT = dict(tuple((i[1],i[0]) for i in CAA_TYPE_CHOICES))

class CAA_Record(models.Model):
    domain = models.ForeignKey(
        Domain,
        verbose_name=_("Domain"),
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=64,
        null=True, blank=True)
    searchname = models.CharField(
        verbose_name=_("Fully Qualified Domain Name"),
        max_length=255,
        null=True, blank=True)
#    provider = models.CharField(
#        _("Provider"),
#        max_length=1,
#        choices=CAA_PROVIDER_CHOICES)
    type = models.CharField(
        _("Type"),
        max_length=1,
        choices=CAA_TYPE_CHOICES)
    issuer_critical = models.BooleanField(
        verbose_name=_("Issuer Critical"),
        default=False)
    tag = models.CharField(
        verbose_name=_("Tag"),
        max_length=16)
    value = models.CharField(
        verbose_name=_("Value"),
        max_length=1024)
    ttl = models.IntegerField(
        verbose_name=_("Time-to-Live"),
        default=settings.RECORD_TTL)
    serial = models.IntegerField(
        verbose_name=_("Serial Number"),
        default=0)
    source = models.CharField(
        _("Source"),
        max_length=1,
        choices=SOURCE_CHOICES,
        default=SOURCE_ADMIN)
    date_updated = models.DateTimeField(
        verbose_name=_("Date Updated"),
        auto_now=True)
    def __str__(self):
        if self.name:
            return f'{self.name}.{self.domain.name}: {self.tag} {self.value}'
        else:
            return f'{self.domain.name}: {self.tag} {self.value}'
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
        verbose_name = 'CAA Record'
        indexes = [
            models.Index(
                fields = [
                    'type',
                    'domain'],
                name='caa_record_idx'),
        ]
