from django.http import Http404
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.contrib.auth.decorators import user_passes_test


def group(group_name='editor'):
    """
    Returns
        whether the current user belong to a group or not
        in case they aren't, they are redirected to the login page
        Returns True always for superusers

    Params
        group_name: name of the group to be matched(default:editor)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser or User.objects.filter(id=request.user.id, groups__name=group_name).exists():
                return func(request, *args, **kwargs)

            messages.warning(
                request, 'You are not allowed to enter into this part of the world of hackers')

            return redirect('login')

        return wrapper
    return decorator


def require_superuser(func):
    """Redirects non superusers to a 404 page"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404

        return func(request, *args, **kwargs)
        # return user_passes_test(func)

    return wrapper
