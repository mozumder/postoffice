from decouple import config

run_env = config('DJANGO_RUN_ENV', default='development').lower()

from .base import *

if run_env == "production":
    from .production import *
elif run_env == "staging":
    from .staging import *
elif run_env == "development":
    from .development import *
elif run_env == "testing":
    from .testing import *
