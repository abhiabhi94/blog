from collections import namedtuple

from django import template

register = template.Library()

DEFAULT_USERNAME = 'thehackadda'


@register.inclusion_tag('footer_social.html', takes_context=True)
def footer_socials(context):
    Socials = namedtuple('Social', ['name', 'link', 'username'])

    socials = (
        ('Facebook', 'https://facebook.com', DEFAULT_USERNAME),
        ('Twitter', 'https://twitter.com', DEFAULT_USERNAME),
        ('Instagram', 'https://instagram.com', 'hackadda'),
        ('Telegram', 'https://telegram.org', DEFAULT_USERNAME),
        ('LinkedIn', 'https://linkedin.com/company', DEFAULT_USERNAME)
        ('RSS Feed', 'http://hackadda.com/latest/feed')
    )
    footers = [Socials(*social) for social in socials]
    context = {
        'footers': footers
    }

    return context
