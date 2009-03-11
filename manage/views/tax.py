# python imports
import urllib

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.catalog.models import Product
from lfs.tax.models import Tax

class TaxForm(ModelForm):
    """Form to add and edit a tax.
    """
    class Meta:
        model = Tax

@permission_required("manage_shop", login_url="/login/")
def manage_taxes(request):
    """Dispatches to the first tax or to the add tax form.
    """
    try:
        tax = Tax.objects.all()[0]
        url = reverse("lfs_manage_tax", kwargs={"id": tax.id})
    except IndexError:
        url = reverse("lfs_add_tax")
    
    return HttpResponseRedirect(url)

@permission_required("manage_shop", login_url="/login/")
def manage_tax(request, id, template_name="manage/tax/tax.html"):
    """Displays the main form to manage taxes.
    """
    tax = get_object_or_404(Tax, pk=id)
    if request.method == "POST":
        form = TaxForm(instance=tax, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            url = reverse("lfs_manage_tax", kwargs={"id" : tax.id})
            response = HttpResponseRedirect(url)            
            
            msg = urllib.quote(_(u"Tax has been saved."))
            response.set_cookie("message", msg)            
            
            return response            
    else:
        form = TaxForm(instance=tax)
    
    return render_to_response(template_name, RequestContext(request, {
        "tax" : tax,
        "taxes" : Tax.objects.all(),
        "form" : form,
        "current_id" : int(id),
    }))

@permission_required("manage_shop", login_url="/login/")
def add_tax(request, template_name="manage/tax/add_tax.html"):
    """Provides a form to add a new tax.
    """
    if request.method == "POST":
        form = TaxForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            tax = form.save()

            url = reverse("lfs_manage_tax", kwargs={"id" : tax.id})
            response = HttpResponseRedirect(url)                        
            msg = urllib.quote(_(u"Tax has been added."))
            response.set_cookie("message", msg)            
            
            return response
    else:
        form = TaxForm()

    return render_to_response(template_name, RequestContext(request, {
        "form" : form,
        "taxes" : Tax.objects.all(),        
    }))

@permission_required("manage_shop", login_url="/login/")
def delete_tax(request, id):
    """Deletes tax with passed id.
    """
    tax = get_object_or_404(Tax, pk=id)
    
    # First remove the tax from all products.
    for product in Product.objects.filter(tax=id):
        product.tax = None
        product.save()
        
    tax.delete()
    
    response = HttpResponseRedirect(reverse("lfs_manage_taxes"))
    
    msg = urllib.quote(_(u"Tax has been deleted."))
    response.set_cookie("message", msg)            
            
    return response
    