from .base import *
from subprocess import getoutput
import urllib.request
from urllib.error import URLError

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

IP_PRIVATE = getoutput('hostname -I').strip()
try:
    IP_PUBLIC = urllib.request.urlopen(
        'https://ident.me').read().decode('utf8')
    ALLOWED_HOSTS.append(IP_PUBLIC)

    print(
        f'You may connect using: {IP_PUBLIC}, {IP_PRIVATE}, localhost')

except URLError:
    print('Not connected to internet, the developement server will not be accessible from outside')

finally:
    ALLOWED_HOSTS.append(IP_PRIVATE)


DEBUG = True

print(ALLOWED_HOSTS)

# Add debug_toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ALLOWED_HOSTS

'''
Change this in future for migration to mysql database
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
