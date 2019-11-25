import os
import json

try:
    from .prod import *
    with open(CONFIG_FILE) as config_file:
        config = json.load(config_file)
        config['PROD']


except KeyError:
    from .dev import *

SECRET_KEY = config['SECRET_KEY']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
