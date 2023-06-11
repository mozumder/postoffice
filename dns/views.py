import base64
import asyncio
import asyncpg
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
from .utilities.server.db import DBConnectInit
from django.apps import apps
from .utilities.server.query import Query

class ip_address(View):
    @staticmethod
    def get_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    def get(self, request, *args, **kwargs):
        ip = self.get_ip(request)
        response = HttpResponse(f'{ip}', content_type="text/plain")
        response['ip'] = ip
        return response

class dns_query(View):

    def get(self, request, *args, **kwargs):

        data = base64.urlsafe_b64decode(request.GET.get('dns')+'====')
        
        #temporary until moved to apps.DnsConfig. Don't need to create a pool of connections on each request
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        db_host = settings.DATABASES['default']['HOST']
        db_port = settings.DATABASES['default']['PORT']
        dsn = f'postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        db_pool = loop.run_until_complete(asyncpg.create_pool(dsn,init=DBConnectInit))

        result = loop.run_until_complete(Query(db_pool, data))
        response = HttpResponse(result, content_type="application/dns-message")
        return response
