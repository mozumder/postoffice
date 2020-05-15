# The files in this directory are from the Django-Vmail package: https://github.com/lgunsch/django-vmail/tree/master/vmail
# These are included here per license given under MIT License for that package.

from django.contrib import admin

# Register your models here.

from .models import Domain, MailUser, Alias


class DomainAdmin(admin.ModelAdmin):
    fields = ['user', 'fqdn', 'active']
    list_display = ['user', 'fqdn', 'active', 'created']
    list_filter = ['user', 'fqdn', 'active', 'created']
    search_fields = ['user', 'fqdn', 'active', 'created']
    date_hierarchy = 'created'

admin.site.register(Domain, DomainAdmin)


class MailUserAdmin(admin.ModelAdmin):
    fields = ['username', 'domain', 'active', 'shadigest', 'salt']
    list_display = ['username', 'domain', 'active', 'created']
    list_filter = ['username', 'domain', 'active', 'created']
    search_fields = ['username', 'domain__fqdn', 'active', 'created']
    date_hierarchy = 'created'

admin.site.register(MailUser, MailUserAdmin)


class AliasAdmin(admin.ModelAdmin):
    fields = ['domain', 'source', 'active', 'destination']
    list_display = ['source', 'destination', 'domain', 'active', 'created']
    list_filter = ['domain', 'active', 'created']
    search_fields = ['source', 'destination', 'domain__fqdn', 'active', 'created']
    date_hierarchy = 'created'

admin.site.register(Alias, AliasAdmin)
