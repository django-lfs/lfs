# django imports
from django.contrib.auth.decorators import permission_required
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs.imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.core.utils import LazyEncoder

@permission_required("manage_shop", login_url="/login/")
def manage_related_products(
    request, product_id, template_name="manage/product/related_products.html"):
    """
    """
    product = Product.objects.get(pk=product_id)
    inline = manage_related_products_inline(request, product_id, as_string=True)
    
    return render_to_string(template_name, RequestContext(request, {
        "product" : product,
        "related_products_inline" : inline,
    }))

# Actions
@permission_required("manage_shop", login_url="/login/")
def manage_related_products_inline(
    request, product_id, as_string=False, template_name="manage/product/related_products_inline.html"):
    """View which shows all related products for the product with the passed id.
    """
    product = Product.objects.get(pk=product_id)
    related_products = product.related_products.all()
    related_products_ids = [p.id for p in related_products]
    
    r = request.REQUEST
    s = request.session
    
    # If we get the parameter ``keep-filters`` or ``page`` we take the 
    # filters out of the request resp. session. The request takes precedence.
    # The page parameter is given if the user clicks on the next/previous page 
    # links. The ``keep-filters`` parameters is given is the users adds/removes
    # products. In this way we keeps the current filters when we needed to. If 
    # the whole page is reloaded there is no ``keep-filters`` or ``page`` and 
    # all filters are reset as they should.
    
    if r.get("keep-filters") or r.get("page"):
        page = r.get("page", s.get("related_products", 1))
        filter_ = r.get("filter", s.get("filter"))
        category_filter = r.get("related_products_category_filter",
                          s.get("related_products_category_filter"))
    else:        
        page = r.get("page", 1)
        filter_ = r.get("filter")
        category_filter = r.get("related_products_category_filter")
    
    # The current filters are saved in any case for later use.
    s["related_products_page"] = page
    s["filter"] = filter_
    s["related_products_category_filter"] = category_filter
    
    filters = Q()
    if filter_:
        filters &= Q(name__icontains = filter_)
    if category_filter:
        if category_filter == "None":
            filters &= Q(categories=None)
        else:
            # First we collect all sub categories and using the `in` operator
            category = lfs_get_object_or_404(Category, pk=category_filter)
            categories = [category]
            categories.extend(category.get_all_children())    
            filters &= Q(categories__in = categories)
    
    products = Product.objects.filter(filters).exclude(pk__in = related_products_ids)        
    paginator = Paginator(products, 6)
    
    total = products.count()
    try:
        page = paginator.page(page)
    except EmptyPage:
        page = 0
    
    result = render_to_string(template_name, RequestContext(request, {
        "product" : product,
        "related_products" : related_products,
        "total" : total,
        "page" : page,
        "paginator" : paginator,
        "filter" : filter_
    }))
    
    if as_string: 
        return result
    else:
        return HttpResponse(result)

@permission_required("manage_shop", login_url="/login/")
def add_related_products(request, product_id):
    """Adds passed related products (by request body) to product with passed id.
    """
    parent_product = Product.objects.get(pk=product_id)
    
    for temp_id in request.POST.keys():

        if temp_id.startswith("product") == False:
            continue
        
        temp_id = temp_id.split("-")[1]
        parent_product.related_products.add(temp_id)
        
        # This isn't necessary but it cleans the cache. See lfs.cache listeners
        # for more
        parent_product.save()
    
    inline = manage_related_products_inline(request, product_id, as_string=True)    
    result = simplejson.dumps({
        "html" : inline,
        "message" : _(u"Related products have been added.")
    }, cls=LazyEncoder);
    
    return HttpResponse(result)

@permission_required("manage_shop", login_url="/login/") 
def remove_related_products(request, product_id):
    """Removes passed related products from product with passed id.
    """
    parent_product = Product.objects.get(pk=product_id)
    
    for temp_id in request.POST.keys():
        
        if temp_id.startswith("product") == False:
            continue
        
        temp_id = temp_id.split("-")[1]
        parent_product.related_products.remove(temp_id)
        
        # This isn't necessary but it cleans the cache. See lfs.cache listeners
        # for more
        parent_product.save()
    
    inline = manage_related_products_inline(request, product_id, as_string=True)
    result = simplejson.dumps({
        "html" : inline,
        "message" : _(u"Related products have been removed.")
    }, cls=LazyEncoder);
    
    return HttpResponse(result)

@permission_required("manage_shop", login_url="/login/")
def update_related_products(request, product_id):
    """Updates related products.
    """
    product = Product.objects.get(pk=product_id)
    if request.POST.get("active_related_products"):
        product.active_related_products = True
    else:
        product.active_related_products = False
    product.save()
    
    inline = manage_related_products_inline(request, product_id, as_string=True)    
    result = simplejson.dumps({
        "html" : inline,
        "message" : _(u"Related products have been updated.")
    }, cls=LazyEncoder);
    
    return HttpResponse(result)
