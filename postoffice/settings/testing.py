from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'test_'+config('POSTGRES_DB'), # Or path to database file if using sqlite3.
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PW'),
        'HOST': config('POSTGRES_HOST',default='localhost'), # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': config('POSTGRES_PORT',default=None), # Set to empty string for default.
        'CONN_MAX_AGE': None,
    }
}

