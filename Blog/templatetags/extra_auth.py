from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name='editor'):
    """
    Returns
        bool
            Whether the given group has the current user or not. 

    Params
        user: obj
            current user
        group: str
            group name to be searched for

    {% request.user|has_group:"Editor" %} -> This will return True if the current user is part of the group Editor,\
    otherwise False.
    """
    # try:
    #     group = Group.objects.get(name=group_name)
    # except Group.DoesNotExist:
    #     return False
    return user.is_superuser or User.objects.filter(id=user.id, groups__name=group_name).exists()
