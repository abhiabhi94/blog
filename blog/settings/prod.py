from subprocess import getoutput
import urllib.request
from urllib.error import URLError
from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import sys

Integrating sentry sdk inside django
sentry_sdk.init(
    dsn="https://782c4ab18f3645bcb343911c744fbb86@sentry.io/1868228",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

# global ALLOWED_HOSTS
# ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# # Add debug_toolbar
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ALLOWED_HOSTS


# def add_ip_to_host(port=8000):
#     '''
#     Returns
#         None

#     Args:
#         port which handles the request
#     Add local IPv4 and public IP addresses to ALLOWED_HOST
#     '''

#     IP_PRIVATE = getoutput('hostname -I').strip()
#     try:
#         IP_PUBLIC = urllib.request.urlopen(
#             'https://ident.me').read().decode('utf8')
#         ALLOWED_HOSTS.append(IP_PUBLIC)

#     except URLError:
#         print('Not connected to internet, the developement server will not be accessible from outside')

#     finally:
#         ALLOWED_HOSTS.append(IP_PRIVATE)
#         print('You may connect at any of the following:')
#         [print(f'http://{i}:{port}') for i in ALLOWED_HOSTS]
#         # Just add a blank file after the allowed addresses
#         print()


# try:
#     host = sys.argv[2]
#     if '0.0.0.0' in host:
#         add_ip_to_host(port=host.split(':')[-1])
# except IndexError:
#     pass

# add_ip_to_host()

DEBUG = False
ALLOWED_HOSTS = ['hackadda.com', '142.93.221.60', 'www.hackadda.com', ]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
