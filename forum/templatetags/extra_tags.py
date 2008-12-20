import math
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

GRAVATAR_TEMPLATE = ('<img width="%(size)s" height="%(size)s" '
                     'src="http://www.gravatar.com/avatar/%(gravatar_hash)s'
                     '?s=%(size)s&d=identicon&r=PG">')

@register.simple_tag
def gravatar(user, size):
    """
    Creates an ``<img>`` for a user's Gravatar with a given size.

    This tag can accept a User object, or a dict containing the
    appropriate values.
    """
    try:
        gravatar = user['gravatar']
    except (TypeError, AttributeError, KeyError):
        gravatar = user.gravatar
    return mark_safe(GRAVATAR_TEMPLATE % {
        'size': size,
        'gravatar_hash': gravatar,
    })

MAX_FONTSIZE = 18
MIN_FONTSIZE = 11
@register.simple_tag
def tag_font_size(max_size, min_size, current_size):
    weight = (math.log10(current_size) - math.log10(min_size)) / (math.log10(max_size) - math.log10(min_size))
    return MIN_FONTSIZE + round((MAX_FONTSIZE - MIN_FONTSIZE) * weight)
