import time
import datetime
import math
import logging
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
    """
    do a logarithmic mapping calcuation for a proper size for tagging cloud
    Algorithm from http://blogs.dekoh.com/dev/2007/10/29/choosing-a-good-font-size-variation-algorithm-for-your-tag-cloud/
    """
    #avoid invalid calculation
    if current_size == 0:
        current_size = 1
    try:
        weight = (math.log10(current_size) - math.log10(min_size)) / (math.log10(max_size) - math.log10(min_size))
    except:
        weight = 0
    return MIN_FONTSIZE + round((MAX_FONTSIZE - MIN_FONTSIZE) * weight)

    
LEADING_PAGE_RANGE_DISPLAYED = TRAILING_PAGE_RANGE_DISPLAYED = 5
LEADING_PAGE_RANGE = TRAILING_PAGE_RANGE = 4
NUM_PAGES_OUTSIDE_RANGE = 1 
ADJACENT_PAGES = 2
@register.inclusion_tag("paginator.html")
def cnprog_paginator(context):
    """
    custom paginator tag
    Inspired from http://blog.localkinegrinds.com/2007/09/06/digg-style-pagination-in-django/
    """
    if (context["is_paginated"]):
        " Initialize variables "
        in_leading_range = in_trailing_range = False
        pages_outside_leading_range = pages_outside_trailing_range = range(0)
 
        if (context["pages"] <= LEADING_PAGE_RANGE_DISPLAYED):
            in_leading_range = in_trailing_range = True
            page_numbers = [n for n in range(1, context["pages"] + 1) if n > 0 and n <= context["pages"]]           
        elif (context["page"] <= LEADING_PAGE_RANGE):
            in_leading_range = True
            page_numbers = [n for n in range(1, LEADING_PAGE_RANGE_DISPLAYED + 1) if n > 0 and n <= context["pages"]]
            pages_outside_leading_range = [n + context["pages"] for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
        elif (context["page"] > context["pages"] - TRAILING_PAGE_RANGE):
            in_trailing_range = True
            page_numbers = [n for n in range(context["pages"] - TRAILING_PAGE_RANGE_DISPLAYED + 1, context["pages"] + 1) if n > 0 and n <= context["pages"]]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
        else: 
            page_numbers = [n for n in range(context["page"] - ADJACENT_PAGES, context["page"] + ADJACENT_PAGES + 1) if n > 0 and n <= context["pages"]]
            pages_outside_leading_range = [n + context["pages"] for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
        return {
            "base_url": context["base_url"],
            "is_paginated": context["is_paginated"],
            "previous": context["previous"],
            "has_previous": context["has_previous"],
            "next": context["next"],
            "has_next": context["has_next"],
            "page": context["page"],
            "pages": context["pages"],
            "page_numbers": page_numbers,
            "in_leading_range" : in_leading_range,
            "in_trailing_range" : in_trailing_range,
            "pages_outside_leading_range": pages_outside_leading_range,
            "pages_outside_trailing_range": pages_outside_trailing_range
        }

@register.inclusion_tag("pagesize.html")
def cnprog_pagesize(context):
    """
    display the pagesize selection boxes for paginator
    """
    if (context["is_paginated"]):
        return {
            "base_url": context["base_url"],
            "pagesize" : context["pagesize"],
            "is_paginated": context["is_paginated"]
        }
        
@register.simple_tag
def get_age(birthday):
    current_time = datetime.datetime(*time.localtime()[0:6])
    diff = current_time - birthday
    return diff.days / 365

@register.simple_tag
def get_total_count(up_count, down_count):
    return up_count + down_count