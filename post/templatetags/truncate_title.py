from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='truncate_title', is_safe=True)
@stringfilter
def truncate_title(val, max_len):
    """
    Returns a truncated_version of value after max_len.
    If the last word doesn't completely fit inside max_len, it is truncated completely.
    Adds ...(ellipsis character) at the end when truncation is done.
    """

    try:
        max_len = int(max_len)
    except ValueError:
        return max_len

    if len(val) > max_len:
        truncated_val = val[:max_len]
        # Check if the next character is a space(This means the word ends here)
        if not val[max_len]:
            truncated_val = val[:val.rfind(' ')]
        return truncated_val + '...'

    return val
