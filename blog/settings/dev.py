from .base import *
from subprocess import getoutput
import urllib.request
from urllib.error import URLError

IP_PRIVATE = getoutput('hostname -I').strip()
try:
    IP_PUBLIC = urllib.request.urlopen(
        'https://ident.me').read().decode('utf8')
    ALLOWED_HOSTS = [IP_PUBLIC]

    print(
        f'You may connect using: {IP_PUBLIC}, {IP_PRIVATE}, localhost')

except URLError:
    print('Not connected to internet, the developement server will not be accessible from outside')

finally:
    ALLOWED_HOSTS.append(IP_PRIVATE)
    ALLOWED_HOSTS.append('localhost')


DEBUG = True

'''
Change this in future for migration to mysql database
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
