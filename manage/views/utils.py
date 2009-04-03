# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

# lfs imports
import lfs.caching.listeners

@permission_required("manage_shop", login_url="/login/")
def utilities(request, template_name="manage/utils.html"):
    """Displays the utility view.
    """
    return render_to_response(template_name, RequestContext(request, {}))
    
def clear_cache(request):
    """Clears the whole cache.
    """
    return lfs.core.utils.set_message_cookie(
        url = reverse("lfs_manage_utils"),
        msg = u"Cache has been cleared.",
    )