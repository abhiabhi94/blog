import os
from subprocess import getoutput
import sys

from urllib.error import URLError
import urllib.request

from .base import *

global ALLOWED_HOSTS
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Add debug_toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ALLOWED_HOSTS


def add_ip_to_host(port):
    """
    Returns
        None

    Args:
        port which handles the request
    Add local IPv4 and public IP addresses to ALLOWED_HOST
    """

    IP_PRIVATE = getoutput('hostname -I').strip().split()
    ALLOWED_HOSTS.extend(IP_PRIVATE)
    try:
        IP_PUBLIC = urllib.request.urlopen(
            'https://ident.me').read().decode('utf8')
        ALLOWED_HOSTS.append(IP_PUBLIC)

    except URLError:
        print('Not connected to internet, the development server will not be accessible from outside')

    finally:
        print('You may connect at any of the following:')
        [print(f'http://{i}:{port}') for i in ALLOWED_HOSTS]
        # Just add a blank file after the allowed addresses
        print()


try:
    host = sys.argv[2].strip()
    if '0.0.0.0' in host:
        add_ip_to_host(port=host.split(':')[-1])

except IndexError:
    pass

DEBUG = True
