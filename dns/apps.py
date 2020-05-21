from django.apps import AppConfig
import asyncio
from django.conf import settings
import asyncpg
from .utilities.server.db import DBConnectInit


class DnsConfig(AppConfig):
    name = 'dns'
    verbose_name = 'DNS'
    hello = 'Nope'
    def ready(self):
        loop = asyncio.get_event_loop()
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        db_host = settings.DATABASES['default']['HOST']
        db_port = settings.DATABASES['default']['PORT']
        dsn = f'postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        self.db_pool = loop.run_until_complete(asyncpg.create_pool(dsn,init=DBConnectInit))
        self.hello = 'Hello World!'
