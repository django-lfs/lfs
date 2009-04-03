# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop
from lfs.core.utils import lfs_quote
from lfs.core.utils import LazyEncoder
from lfs.core.widgets.image import LFSImageInput

class ShopForm(ModelForm):
    """Form to edit shop data.
    """
    def __init__(self, *args, **kwargs):
        super(ShopForm, self).__init__(*args, **kwargs)
        self.fields["image"].widget = LFSImageInput()
    
    class Meta:
        model = Shop
        fields = ("name", "shop_owner", "from_email", "notification_emails", 
            "description", "image", "static_block")

class ShopDefaultValuesForm(ModelForm):
    """
    """

    class Meta:
        model = Shop
        fields = ("product_cols", "product_rows", "category_cols", 
            "default_country", "countries")
    
@permission_required("manage_shop", login_url="/login/")
def manage_shop(request, template_name="manage/shop/shop.html"):
    """Displays the form to manage shop data.
    """
    shop = lfs_get_object_or_404(Shop, pk=1)
    if request.method == "POST":
        form = ShopForm(instance=shop, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            url = reverse("lfs_manage_shop")
            response = HttpResponseRedirect(url)
            
            msg = lfs_quote(_(u"Shop data has been saved."))
            response.set_cookie("message", msg)
            
            return response
    else:
        form = ShopForm(instance=shop)
    
    return render_to_response(template_name, RequestContext(request, {
        "shop" : shop,
        "form" : form,
        "default_values" : default_values_part(request),
    }))

@permission_required("manage_shop", login_url="/login/")    
def default_values_part(request, template_name="manage/shop/default_values.html"):
    """Displays the default value part of the shop form.
    """
    shop = lfs_get_object_or_404(Shop, pk=1)
    
    if request.method == "POST":
        form = ShopDefaultValuesForm(instance=shop, data=request.POST)
    else:
        form = ShopDefaultValuesForm(instance=shop)
    
    return render_to_string(template_name, RequestContext(request, {
        "shop" : shop,
        "form" : form,
    }))

def save_default_values(request):
    """Saves the default value part
    """
    shop = lfs_get_object_or_404(Shop, pk=1)
    form = ShopDefaultValuesForm(instance=shop, data=request.POST)
    
    if form.is_valid():
        form.save()    
        message = _(u"Shop default values have been saved.")
    else:
        message = _(u"Please correct the indicated errors.")
    
    result = simplejson.dumps({
        "html" : default_values_part(request),
        "message" : message
    }, cls = LazyEncoder)
    
    return HttpResponse(result)    