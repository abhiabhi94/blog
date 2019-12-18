import os
import json

CONFIG_FILE = '/etc/config.json'

try:
    with open(CONFIG_FILE) as config_file:
        config = json.load(config_file)
        config['PROD']
    from .prod import *


except KeyError:
    from .dev import *

SECRET_KEY = config['SECRET_KEY']

DATABASES = {
    'default': {
        'NAME':'blog',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'blogadmin',
        'PASSWORD': 'Krishnajha987@',
        'HOST': 'localhost',
        'OPTIONS':{
            'autocommit': True,
        }
    }
}
