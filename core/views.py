# django imports
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader
from django.template import RequestContext

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop

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
    try:
        from_email = settings.ADMINS[0][1]
        to_emails = [a[1] for a in settings.ADMINS]
    except IndexError:
        pass
    else:
        mail = EmailMessage(
            subject="Error LFS", body=request, from_email=from_email, to=to_emails)
        mail.send(fail_silently=True)
        
    t = loader.get_template('500.html')
    c = RequestContext(request)
    return HttpResponse(t.render(c), status=500)