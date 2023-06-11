from django.contrib import admin

# Register your models here.
from .models import FileRule


class FileRuleAdmin(admin.ModelAdmin):
    fields = ['mailbox', 'field', 'contains', 'folder']
    list_display = ['mailbox', 'field', 'contains', 'folder']
    list_filter = ['mailbox', 'field', 'contains', 'folder']
    search_fields = ['field', 'contains', 'folder']
    date_hierarchy = 'created'

admin.site.register(FileRule, FileRuleAdmin)
