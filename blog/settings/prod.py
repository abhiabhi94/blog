import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F401, F403

# This part should only be uncommented when testing something bad in production.

# global ALLOWED_HOSTS
# DEBUG = True
# ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# # Add debug_toolbar
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ALLOWED_HOSTS


# def add_ip_to_host(port=8000):
#     """
#     Returns
#         None

#     Args:
#         port which handles the request
#     Add local IPv4 and public IP addresses to ALLOWED_HOST
#     """
#     import sys
#     from subprocess import getoutput
#     from urllib.error import URLError
#     import urllib.request

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
###############################

# Uncomment code below this line when in production

DEBUG = False
ALLOWED_HOSTS = ['hackadda.com', '142.93.221.60', 'www.hackadda.com', ]

# Enable only if you shift to HTTPS from HTTP
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True  # makes it difficult to hijack user sessions

# prevent the browser from identifying content types incorrectly
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True  # prevents XSS attacks
SECURE_SSL_REDIRECT = True  # Redirect connections to HTTPS

# makes it difficult for network traffic sniffers to steal CSRF token
CSRF_COOKIE_SECURE = True
SECURE_HSTS_PRELOAD = True  # submit your website to the browser preload list
SECURE_HSTS_SECONDS = 3600  # 1 hour. Refuses to connect over HTTP
SECURE_HSTS_INCLUDE_SUBDOMAINS = True


STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Integrating sentry sdk inside django
sentry_sdk.init(
    dsn="https://782c4ab18f3645bcb343911c744fbb86@sentry.io/1868228",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

# enable cute status codes only for production
# since it prevents debug reports in browser for debug mode
MIDDLEWARE.append(  # noqa: F405
    'django_cute_status.middleware.CuteStatusMiddleware',
)

INSTALLED_APPS.append('django_cute_status')  # noqa: F405
