from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Domain, Host, A_Record, IPLog, DynamicDNS
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
    list_display = ['__str__', 'name', domain, 'ip_address', 'ttl', 'date_updated']
    list_display_links = ['__str__',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('name'),
            ('host'),
            ('domain'),
            ('ttl'),
            ('date_updated'),
            ]
        }),
    ]
    readonly_fields=('date_updated',)

@admin.register(IPLog)
class IPLogAdmin(admin.ModelAdmin):
    list_display = ['date_updated','address',]
    list_display_links = ['date_updated',]
    search_fields = ['address']
    fieldsets = [
        (None, {'fields': [
            ('id'),
            ('date_updated','address'),
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
