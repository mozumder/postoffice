from django.contrib import admin

from .models import Mailbox, Message, Envelope

@admin.register(Mailbox)
class MailboxAdmin(admin.ModelAdmin):
    list_display = ['user','name','parent',]
    list_display_links = ['name',]
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('user'),
            ('name'),
            ('parent'),
            ]
        }),
    ]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['mailbox','date','from_address','to_address','subject']
    search_fields = ['from_address','to_address','cc','bcc','subject','body']
    fieldsets = [
        (None, {'fields': [
            ('mailbox'),
            ('date'),
            ('from_address'),
            ('to_address'),
            ('cc'),
            ('bcc'),
            ('subject'),
            ('body'),
            ]
        }),
    ]

@admin.register(Envelope)
class EnvelopeAdmin(admin.ModelAdmin):
    list_display = ['msg','message_id','sender','receiver']
    list_display_links = ['msg',]
    search_fields = ['message_id','sender','receiver',]
    fieldsets = [
        (None, {'fields': [
            ('msg'),
            ('message_id'),
            ('sender'),
            ('receiver'),
            ]
        }),
    ]
