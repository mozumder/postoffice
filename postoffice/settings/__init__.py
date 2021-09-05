from decouple import config

run_env = config('DJANGO_RUN_ENV', default='dev').lower()

from .base import *

if run_env == "prod":
    from .production import *
elif run_env == "dev":
    from .development import *
elif run_env == "test":
    from .testing import *
elif run_env == "staging":
    from .staging import *
