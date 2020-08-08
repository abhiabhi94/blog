import json
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')

CONFIG_FILE = '/etc/config.json'

with open(CONFIG_FILE) as f:
    config = json.load(f)


SECRET_KEY = config['SECRET_KEY']
EMAIL_HOST_USER = config['EMAIL_USER']
EMAIL_HOST_PASSWORD = config['EMAIL_PASS']


application = get_wsgi_application()
