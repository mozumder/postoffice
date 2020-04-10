from .base import *
ENV = None
#from .production import *
try:
    from .production import *
    ENV = 'prod'
except:
    ENV = None

if ENV == None:
    try:
        from .staging import *
        ENV = 'staging'
    except:
        ENV = None

if ENV == None:
    try:
        from .development import *
        ENV = 'dev'
    except:
        ENV = None

