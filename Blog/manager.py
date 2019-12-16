from .models import Post
from django.db.models import F


def hits_decorator(function):
    def wrap(request, *args, **kwargs):
        '''Adds one to the hit field'''
        Post.objects.filter(slug=kwargs.get('slug')).update(hits=F('hits')+1)
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap
