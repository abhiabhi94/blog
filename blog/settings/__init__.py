import os
import json

CONFIG_FILE = '/etc/config.json'
DB_CONFIG_FILE = '/etc/db.cnf'

SECRET_KEY = os.environ['SECRET_KEY']
EMAIL_HOST_USER = os.environ['EMAIL_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_PASS']

# used for testing environment(allows passing throughCI)
if not os.environ.get('TEST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'OPTIONS': {
                'read_default_file': DB_CONFIG_FILE,
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

if os.environ.get('PROD'):
    from .prod import *
else:
    from .dev import *
