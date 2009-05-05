# django imports
from django import template
from django.core.cache import cache

# lfs imports
from lfs.page.models import Page

register = template.Library()

@register.inclusion_tag('page/pages_portlet.html', takes_context=True)
def pages_portlet(context):
    """Displays links to pages.
    """
    cache_key = "pages"
    pages = cache.get(cache_key)
    if pages is None:
        pages = Page.objects.active()
        cache.set(cache_key, pages)
        
    return {"pages" : pages}
