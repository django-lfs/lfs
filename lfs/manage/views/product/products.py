# django imports
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.settings import VARIANT
from lfs.core.utils import LazyEncoder

@permission_required("manage_shop", login_url="/login/")    
def products(request, template_name="manage/product/products.html"):
    """Displays an overview list of all products.
    """
    
    return render_to_response(template_name, RequestContext(request, {
        "products_inline" : products_inline(request, as_string=True),
    }))

@permission_required("manage_shop", login_url="/login/")        
def products_inline(request, as_string=False, template_name="manage/product/products_inline.html"):
    """Displays the list of products.
    """
    page = request.REQUEST.get("page", 1)
    
    # If there is a reset attribute we delete the filter session information
    if request.GET.get("reset-filter"):
        if request.session.has_key("name_filter"):
            del request.session["name_filter"]
        if request.session.has_key("category_filter"):
            del request.session["category_filter"]
    
    # If the request comes from the form (form_sent variable is set) we update 
    # the session information with request information.
    if request.GET.get("form_sent"):
        request.session["name_filter"] = request.GET.get("name_filter")
        request.session["category_filter"] = request.GET.get("category_filter")
    
    # At least we take the filter information always out of the session
    name_filter = request.session.get("name_filter")
    category_filter = request.session.get("category_filter")
    
    filters = Q()
    if name_filter:
        filters &= Q(name__icontains=name_filter)
        
    if category_filter:
        if category_filter == "None":
            filters &= Q(categories=None)
        else:
            # First we collect all sub categories and using the `in` operator
            category = lfs_get_object_or_404(Category, pk=category_filter)
            categories = [category]
            categories.extend(category.get_all_children())
        
            filters &= Q(categories__in = categories)

    products = Product.objects.filter(filters).exclude(sub_type=VARIANT)            
    paginator = Paginator(products, 20)

    try:
        page = paginator.page(int(page))
    except EmptyPage:
        page = 0
    
    if as_string:
        return render_to_string(template_name, RequestContext(request, {
            "page" : page,
            "paginator" : paginator,
        }))
    else:
        return render_to_response(template_name, RequestContext(request, {
            "page" : page,
            "paginator" : paginator,
        }))

# Actions        
@permission_required("manage_shop", login_url="/login/")
def save_products(request):
    """Saves products with passed ids (by request body).
    """
    for key, value in request.POST.items():

        if key.startswith("id-"):
            id = value

            try:
                product = Product.objects.get(pk=id)
            except ObjectDoesNotExist:
                continue
            
            product.name = request.POST.get("name-%s" % id, "")
            product.sku = request.POST.get("sku-%s" % id, "")
            product.slug = request.POST.get("slug-%s" % id, "")
                            
            try:
                product.price = float(request.POST.get("price-%s" % id, 0))
            except ValueError:
                product.price = 0
            try:
                product.for_sale_price = \
                    float(request.POST.get("for_sale_price-%s" % id, 0))
            except ValueError:
                product.for_sale_price = 0
                            
            if request.POST.get("for_sale-%s" % id):
                product.for_sale = True
            else:
                product.for_sale = False

            try:
                product.save()
            except IntegrityError:
                pass
                
    url = reverse("lfs_manage_products")
    return HttpResponseRedirect(url)

        