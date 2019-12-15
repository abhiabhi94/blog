from .models import Post
from django.shortcuts import get_object_or_404

def hits_decorator(function):
    def wrap(request, *args, **kwargs):
        obj = get_object_or_404(Post, slug=kwargs.get('slug'))
        obj.update_counter()
        obj.save()
        return function(request, *args, **kwargs)
    wrap.__doc__  = function.__doc__
    wrap.__name__ = function.__name__
    return wrap