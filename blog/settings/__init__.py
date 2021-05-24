import os

DB_CONFIG_FILE = '/etc/db.cnf'

SECRET_KEY = os.environ.get('SECRET_KEY')
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')

if os.environ.get('PROD'):
    from .prod import *  # noqa: F403
else:
    from .dev import *  # noqa: F403

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
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),  # noqa: F405
        }
    }
