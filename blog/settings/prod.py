from subprocess import getoutput
import urllib.request
from urllib.error import URLError
from .base import *
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

DEBUG = True
ALLOWED_HOSTS = ['hackadda.com', '142.93.221.60', 'www.hackadda.com', ]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
