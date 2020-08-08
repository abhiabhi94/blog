import json
import os

from django.core.wsgi import get_wsgi_application

CONFIG_FILE = '/etc/config.json'

with open(CONFIG_FILE) as f:
    config = json.load(f)


os.environ.setdefault('SECRET_KEY', config['SECRET_KEY'])
os.environ.setdefault('EMAIL_USER', config['EMAIL_USER'])
os.environ.setdefault('EMAIL_PASS', config['EMAIL_PASS'])
os.environ.setdefault('PROD', 'True')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')


application = get_wsgi_application()
