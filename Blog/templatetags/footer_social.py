from collections import namedtuple

from django import template
from django.shortcuts import reverse

register = template.Library()

DEFAULT_USERNAME = 'thehackadda'


@register.simple_tag(name='load_socials')
def load_socials():
    Socials = namedtuple('Social', ['name', 'link'])

    social_info = (
        ('facebook', f'https://facebook.com/{DEFAULT_USERNAME}'),
        ('twitter', f'https://twitter.com/{DEFAULT_USERNAME}'),
        ('instagram', f'https://instagram.com/hackadda'),
        ('telegram', f'https://t.me/{DEFAULT_USERNAME}'),
        ('linkedin', f'https://linkedin.com/company/{DEFAULT_USERNAME}'),
        ('rss', reverse('rss-feed'))
    )
    socials = [Socials(*info) for info in social_info]
    return socials
