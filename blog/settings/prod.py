from .base import *
from subprocess import getoutput
import urllib.request
from urllib.error import URLError

DEBUG = False
ALLOWED_HOSTS = ['hackadda.com', ]

# ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# IP_PRIVATE = getoutput('hostname -I').strip()
# try:
#     IP_PUBLIC = urllib.request.urlopen(
#         'https://ident.me').read().decode('utf8')
#     ALLOWED_HOSTS.append(IP_PUBLIC)

#     print(
#         f'You may connect using: {IP_PUBLIC}, {IP_PRIVATE}, localhost')

# except URLError:
#     print('Not connected to internet, the developement server will not be accessible from outside')

# finally:
#     ALLOWED_HOSTS.append(IP_PRIVATE)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
