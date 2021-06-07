import sys
import urllib.request
from subprocess import getoutput
from urllib.error import URLError

from .base import *  # noqa: F403, F401

global ALLOWED_HOSTS
ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # noqa: F405
INTERNAL_IPS = ALLOWED_HOSTS


def add_ip_to_host(port):
    """
    Returns
        None

    Args:
        port which handles the request
    Add local IPv4 and public IP addresses to ALLOWED_HOST
    """

    ip_private = getoutput('hostname -I').strip().split()
    ALLOWED_HOSTS.extend(ip_private)
    try:
        ip_public = urllib.request.urlopen(
            'https://ident.me').read().decode('utf8')
        ALLOWED_HOSTS.append(ip_public)

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

DEBUG = False
