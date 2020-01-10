from django import template

register = template.Library()


@register.inclusion_tag('footer_social.html', takes_context=True)
def footer_socials(context):
    social
    context = {
        'footer_fb': 'http://facebook.com/thehackadda',
        'footer_twitter': 'https://twitter.com/thehackadda',
        'footer_ig': 'https://instagram.com/hackadda',
    }

    return context
