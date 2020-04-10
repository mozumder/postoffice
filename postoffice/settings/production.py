import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'j41=&#18)&*u05b4n#f7^$u&%a-tp%z317yz6+t+$hav0q=zab'
 
ALLOWED_HOSTS = [ 'mail.mozumder.net', '127.0.0.1', '10.0.1.7']

DEBUG = False
PREPARE_DB = True
MULTIPROCESS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mail_mozumder_net_django',                      # Or path to database file if using sqlite3.
        'USER': 'mail_admin',
        'PASSWORD': 'NGx1w1Hl3iBRvhqrnuDOIyXoHqd641oi',
        'HOST': '127.0.0.1',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
        'CONN_MAX_AGE': None,
        }
}

