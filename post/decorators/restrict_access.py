from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect, reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def require_group(group_name=None):
    """
    Returns
        whether the current user belong to a group or not
        in case they aren't, they are redirected to the login page
        Returns True always for superusers

    Params
        group_name: name of the group to be matched(default:editor)
    """
    if group_name is None:
        group_name = Group.objects.get(name='editor').name

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser or User.objects.filter(id=request.user.id, groups__name=group_name).exists():
                return func(request, *args, **kwargs)

            messages.warning(
                request, _('You are not allowed to enter into this part of the world of hackers'))

            return redirect(reverse('login'))

        return wrapper
    return decorator


def require_superuser(func):
    """Redirects non superusers to a 404 page"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404

        return func(request, *args, **kwargs)

    return wrapper


def require_ajax():
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return func(request, *args, **kwargs)

            return HttpResponseBadRequest(_('Only AJAX requests are allowed'))

        return wrapper
    return decorator
