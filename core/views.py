# django imports
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader
from django.template import RequestContext

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop

# arecibo
from arecibo.wrapper import post

def shop_view(request, template_name="shop/shop.html"):
    """Displays the shop.
    """
    shop = lfs_get_object_or_404(Shop, pk=1)
    return render_to_response(template_name, RequestContext(request, {
        "shop" : shop
    }))
    
def robots(request, template_name="shop/robots.txt"):
    """Displays the robots.txt.
    """
    return render_to_response(template_name)
        
def server_error(request):
    """Own view in order to pass RequestContext and send an error message.
    """
    # post(request, 500)
    
    # mail = EmailMessage(
    #     subject="Error", body=request, from_email="usenet@diefenba.ch", to=["usenet@diefenba.ch"])
    # mail.send(fail_silently=True)
        
    t = loader.get_template('500.html')
    c = RequestContext(request)
    return HttpResponse(t.render(c), status=500)