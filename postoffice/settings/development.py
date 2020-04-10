import os
from pathlib import Path

BASE_DIR = BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = 'of@yfkk1n$eo9k1dga=non5t6n-21d5fpc@o=p28r6^#&!uytu'
DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


