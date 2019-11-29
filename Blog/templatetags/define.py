from django import template
register = template.Library()


@register.simple_tag(name='define')
def define(val=None):
    '''
    Define a "define" tag to be used for assigning values inside a template
    Usage:  {{% load define %}}

    {% define "something" as var %} -> This will store the value "something" within the variable var inside the template.
    '''
    return val
