from .base import *
from subprocess import getoutput
import urllib.request
from urllib.error import URLError
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Integrating sentry sdk inside django
sentry_sdk.init(
    dsn="https://782c4ab18f3645bcb343911c744fbb86@sentry.io/1868228",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

DEBUG = False
# ALLOWED_HOSTS = ['hackadda.com', ]

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

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
