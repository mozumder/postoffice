from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import *
# Register your models here.

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['owner', 'name', 'date_updated']
    list_display_links = ['name',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('owner'),
            ('name'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    def domain(obj):
        if obj.domain:
            url = reverse('admin:dns_domain_change', args = [obj.domain.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.domain.__str__())
        else:
            html = format_html("-")
        return html
    list_display = ['name',domain, 'date_updated']
    list_display_links = ['name',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('name'),
            ('domain'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(SOA_Record)
class SOA_RecordAdmin(admin.ModelAdmin):
    def host(obj):
        if obj.host:
            url = reverse('admin:dns_host_change', args = [obj.host.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.host.host_name())
        else:
            html = format_html("-")
        return html
    def domain(obj):
        if obj.domain:
            url = reverse('admin:dns_domain_change', args = [obj.domain.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.domain.__str__())
        else:
            html = format_html("-")
        return html
    list_display = ['__str__', domain, 'origin', 'rname', 'nameserver', 'refresh', 'retry', 'expiry', 'nxttl', 'ttl', 'serial', 'date_updated']
    list_display_links = ['__str__',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('domain'),
            ('origin'),
            ('rname'),
            ('nameserver'),
            ('nameserver_host'),
            ('refresh'),
            ('retry'),
            ('expiry'),
            ('nxttl'),
            ('ttl'),
            ('serial'),
            ('source'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(A_Record)
class A_RecordAdmin(admin.ModelAdmin):
    def host(obj):
        if obj.host:
            url = reverse('admin:dns_host_change', args = [obj.host.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.host.host_name())
        else:
            html = format_html("-")
        return html
    def domain(obj):
        if obj.domain:
            url = reverse('admin:dns_domain_change', args = [obj.domain.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.domain.__str__())
        else:
            html = format_html("-")
        return html
    list_display = ['__str__', domain, 'name', 'ip_address', 'ttl', 'roundrobin', 'dynamic_ip', 'serial', 'date_updated']
    list_display_links = ['__str__',]
    list_editable = ['dynamic_ip',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('domain'),
            ('name'),
            ('fqdn'),
            ('ip_address'),
            ('dynamic_ip'),
            ('roundrobin'),
            ('host'),
            ('ttl'),
            ('serial'),
            ('source'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(AAAA_Record)
class AAAA_RecordAdmin(admin.ModelAdmin):
    def host(obj):
        if obj.host:
            url = reverse('admin:dns_host_change', args = [obj.host.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.host.host_name())
        else:
            html = format_html("-")
        return html
    def domain(obj):
        if obj.domain:
            url = reverse('admin:dns_domain_change', args = [obj.domain.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.domain.__str__())
        else:
            html = format_html("-")
        return html
    list_display = ['__str__', domain, 'name', 'ip_address', 'ttl', 'serial', 'date_updated']
    list_display_links = ['__str__',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('domain'),
            ('name'),
            ('fqdn'),
            ('ip_address'),
            ('host'),
            ('ttl'),
            ('serial'),
            ('source'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(CNAME_Record)
class CNAME_RecordAdmin(admin.ModelAdmin):
    def host(obj):
        if obj.host:
            url = reverse('admin:dns_host_change', args = [obj.host.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.host.host_name())
        else:
            html = format_html("-")
        return html
    def domain(obj):
        if obj.domain:
            url = reverse('admin:dns_domain_change', args = [obj.domain.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.domain.__str__())
        else:
            html = format_html("-")
        return html
    list_display = ['__str__', domain, 'name', 'canonical_name', 'ttl', 'serial', 'date_updated']
    list_display_links = ['__str__',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('domain'),
            ('name'),
            ('fqdn'),
            ('canonical_name'),
            ('host'),
            ('ttl'),
            ('serial'),
            ('source'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(MX_Record)
class MX_RecordAdmin(admin.ModelAdmin):
    def host(obj):
        if obj.host:
            url = reverse('admin:dns_host_change', args = [obj.host.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.host.host_name())
        else:
            html = format_html("-")
        return html
    def domain(obj):
        if obj.domain:
            url = reverse('admin:dns_domain_change', args = [obj.domain.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.domain.__str__())
        else:
            html = format_html("-")
        return html
    list_display = ['__str__', domain, 'name', 'host', 'preference', 'ttl', 'serial', 'date_updated']
    list_display_links = ['__str__',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('domain'),
            ('name'),
            ('fqdn'),
            ('hostname'),
            ('host'),
            ('preference'),
            ('ttl'),
            ('serial'),
            ('source'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(TXT_Record)
class TXT_RecordAdmin(admin.ModelAdmin):
    def host(obj):
        if obj.host:
            url = reverse('admin:dns_host_change', args = [obj.host.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.host.host_name())
        else:
            html = format_html("-")
        return html
    def domain(obj):
        if obj.domain:
            url = reverse('admin:dns_domain_change', args = [obj.domain.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.domain.__str__())
        else:
            html = format_html("-")
        return html
    list_display = ['__str__', domain, 'name', 'value', 'ttl', 'serial', 'date_updated']
    list_display_links = ['__str__',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('domain'),
            ('name'),
            ('fqdn'),
            ('value'),
            ('ttl'),
            ('serial'),
            ('source'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(PTR_Record)
class PTR_RecordAdmin(admin.ModelAdmin):
    def host(obj):
        if obj.host:
            url = reverse('admin:dns_host_change', args = [obj.host.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.host.host_name())
        else:
            html = format_html("-")
        return html
    def domain(obj):
        if obj.domain:
            url = reverse('admin:dns_domain_change', args = [obj.domain.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.domain.__str__())
        else:
            html = format_html("-")
        return html
    list_display = ['__str__', domain, 'name', 'hostname', 'ttl', 'serial', 'date_updated']
    list_display_links = ['__str__',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('domain'),
            ('name'),
            ('fqdn'),
            ('hostname'),
            ('host'),
            ('ttl'),
            ('serial'),
            ('source'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(NS_Record)
class NS_RecordAdmin(admin.ModelAdmin):
    def host(obj):
        if obj.host:
            url = reverse('admin:dns_host_change', args = [obj.host.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.host.host_name())
        else:
            html = format_html("-")
        return html
    def domain(obj):
        if obj.domain:
            url = reverse('admin:dns_domain_change', args = [obj.domain.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.domain.__str__())
        else:
            html = format_html("-")
        return html
    list_display = ['__str__', domain, 'name', 'delegate', 'ttl', 'serial', 'date_updated']
    list_display_links = ['__str__',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('domain'),
            ('name'),
            ('fqdn'),
            ('delegate'),
            ('delegate_host'),
            ('ttl'),
            ('serial'),
            ('source'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(SRV_Record)
class SRV_RecordAdmin(admin.ModelAdmin):
    def host(obj):
        if obj.host:
            url = reverse('admin:dns_host_change', args = [obj.host.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.host.host_name())
        else:
            html = format_html("-")
        return html
    def domain(obj):
        if obj.domain:
            url = reverse('admin:dns_domain_change', args = [obj.domain.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.domain.__str__())
        else:
            html = format_html("-")
        return html
    list_display = ['__str__', domain, 'name', 'priority', 'weight', 'port', 'host_name', 'ttl', 'serial', 'date_updated']
    list_display_links = ['__str__',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('domain'),
            ('name'),
            ('fqdn'),
            ('priority'),
            ('weight'),
            ('port'),
            ('host_name'),
            ('host'),
            ('ttl'),
            ('serial'),
            ('source'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)


@admin.register(CAA_Record)
class CAA_RecordAdmin(admin.ModelAdmin):
    def host(obj):
        if obj.host:
            url = reverse('admin:dns_host_change', args = [obj.host.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.host.host_name())
        else:
            html = format_html("-")
        return html
    def domain(obj):
        if obj.domain:
            url = reverse('admin:dns_domain_change', args = [obj.domain.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.domain.__str__())
        else:
            html = format_html("-")
        return html
    list_display = ['__str__', domain, 'name', 'type', 'issuer_critical', 'tag', 'value', 'ttl', 'serial', 'date_updated']
    list_display_links = ['__str__',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('domain'),
            ('name'),
            ('fqdn'),
            ('type'),
            ('issuer_critical'),
            ('tag'),
            ('value'),
            ('ttl'),
            ('serial'),
            ('source'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(IPLog)
class IPLogAdmin(admin.ModelAdmin):
    list_display = ['date_updated','ip',]
    list_display_links = ['date_updated',]
    search_fields = ['ip']
    fieldsets = [
        (None, {'fields': [
            ('ip'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(DynamicDNSAccount)
class DynamicDNSAccountAdmin(admin.ModelAdmin):
    list_display = ['owner', 'username', 'password', 'endpoint', 'date_updated']
    list_display_links = ['username',]
    search_fields = ['username']
    fieldsets = [
        (None, {'fields': [
            ('owner'),
            ('username', 'password'),
            ('endpoint'),
            ('date_updated'),
            ('domains'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)


@admin.register(DynamicDNS)
class DynamicDNSAdmin(admin.ModelAdmin):
    list_display = ['a_record', 'dyndns_id','password']
    list_display_links = ['a_record',]
    search_fields = ['a_record','dyndns_id']
    fieldsets = [
        (None, {'fields': [
            ('a_record'),
            ('dyndns_id'),
            ('password'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)
