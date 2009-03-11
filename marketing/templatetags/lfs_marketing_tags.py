# django imports
from django import template
from django.core.cache import cache

# lfs imports
import lfs.marketing.utils

register = template.Library()

@register.inclusion_tag('marketing/topseller_portlet.html', takes_context=True)
def topseller_portlet(context, limit):
    """Displays topseller
    """
    cache_key = "topseller"
    topseller = cache.get(cache_key)

    if topseller is None:
        topseller = lfs.marketing.utils.get_topseller(limit)
        cache.set("topseller", topseller)
        
    return {
        "topseller" : topseller,
    }
