# django imports
from django.shortcuts import render_to_response
from django.template import RequestContext

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.page.models import Page

def page_view(request, slug, template_name="page/page.html"):
    """Displays page with passed slug
    """
    page = lfs_get_object_or_404(Page, slug=slug)
    
    return render_to_response(template_name, RequestContext(request, {
        "page" : page
    }))