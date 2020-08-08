import os

import django
from django.core.handlers.wsgi import WSGIHandler


class WSGIEnvironment(WSGIHandler):

    def __call__(self, environ, start_response):

        os.environ['EMAIL_USER'] = environ['EMAIL_USER']
        os.environ['EMAIL_PASS'] = environ['EMAIL_PASS']
        os.environ['SECRET_KEY'] = environ['SECRET_KEY']
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog.settings")
        django.setup()
        return super(WSGIEnvironment, self).__call__(environ, start_response)


application = WSGIEnvironment()
