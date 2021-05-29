import os

from .base import *  # noqa: F401, F403

if os.environ.get('PROD'):
    from .prod import *  # noqa: F403
else:
    from .dev import *  # noqa: F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': DB_CONFIG_FILE,  # noqa: F405
        },
    }
}
