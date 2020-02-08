from datetime import timedelta
from django import template
from django.utils import timezone
from django.utils.timesince import timesince

register = template.Library()


@register.filter(name='cool_timesince', is_safe=False)
def cool_timesince(val, now=1):
    """
    Converts the time into a more human readable format.
    It makes uses of django's {timesince} template and removes the extra information from it.

    Returns:
      str: time in a more human readable format.

    Params:
        val: a datetime object
        now: int 
            a constraint in ***minutes*** that decides for upto what values 'Just now' will be returned. 
    """
    if not val:
        return ''
    current_time = timezone.now()
    try:
        diff = current_time - val
    except (ValueError, TypeError):
        return val
    # print('difference:', diff)
    if diff <= timedelta(minutes=now):
        return 'Just now'

    return f'{timesince(val).split(", ")[0]} ago'
