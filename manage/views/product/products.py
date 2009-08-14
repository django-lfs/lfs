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
    product_filters = request.session.get("product-filters", {})
    products = _get_filtered_products(request, product_filters)

    paginator = Paginator(products, 20)

    page = request.REQUEST.get("page", 1)
    page = paginator.page(page)

    result = render_to_string(template_name, RequestContext(request, {
        "page" : page,
        "paginator" : paginator,
        "active" : product_filters.get("active", ""),
        "name" : product_filters.get("name", ""),
        "category" : product_filters.get("category", ""),
        "price" : product_filters.get("price", ""),
        "for_sale" : product_filters.get("for_sale", ""),
        "sub_type" : product_filters.get("sub_type", ""),
    }))

    if as_string:
        return result
    else:
        html = (("#products-inline", result),)

        result = simplejson.dumps({
            "html" : html,
        }, cls = LazyEncoder)

        return HttpResponse(result)

# Actions
@permission_required("manage_shop", login_url="/login/")
def reset_filters(request):
    """Resets all product filters.
    """
    if request.session.has_key("product-filters"):
        del request.session["product-filters"]

    if request.REQUEST.get("came-from") == "product":
        product_id = request.REQUEST.get("product-id")
        html = (
            ("#selectable-products-inline", selectable_products_inline(request, as_string=True)),
            ("#product-inline", product_inline(request, product_id=product_id, as_string=True)),
        )
    else:
        html = (("#products-inline", products_inline(request, as_string=True)),)

    msg = _(u"Product filters have been reset")

    result = simplejson.dumps({
        "html" : html,
        "message" : msg,
    }, cls = LazyEncoder)

    return HttpResponse(result)

@permission_required("manage_shop", login_url="/login/")
def set_filters(request):
    """Sets product filters given by passed request.
    """
    product_filters = request.session.get("product-filters", {})
    
    for name in ("name", "active", "price", "category", "for_sale", "sub_type"):
        if request.POST.get(name, "") != "":
            product_filters[name] = request.POST.get(name)
        else:
            if product_filters.get(name):
                del product_filters[name]

    request.session["product-filters"] = product_filters

    if request.REQUEST.get("came-from") == "product":
        product_id = request.REQUEST.get("product-id")
        html = (
            ("#selectable-products-inline", selectable_products_inline(request, as_string=True)),
            ("#product-inline", product_inline(request, product_id=product_id, as_string=True)),
        )
    else:
        html = (("#products-inline", products_inline(request, as_string=True)),)

    msg = _(u"Product filters have been set")

    result = simplejson.dumps({
        "html" : html,
        "message" : msg,
    }, cls = LazyEncoder)

    return HttpResponse(result)

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

            if request.POST.get("active-%s" % id):
                product.active = True
            else:
                product.active = False

            try:
                product.save()
            except IntegrityError:
                pass

    html = (("#products-inline", products_inline(request, as_string=True)),)
    msg = _(u"Products have been saved")

    result = simplejson.dumps({
        "html" : html,
        "message" : msg,
    }, cls = LazyEncoder)

    return HttpResponse(result)

def _get_filtered_products(request, product_filters):
    """
    """
    products = Product.objects.all()
    product_ordering = request.session.get("product-ordering", "id")
    product_ordering_order = request.session.get("product-ordering-order", "")

    # Filter
    name = product_filters.get("name", "")
    if name != "":
        products = products.filter(name__icontains=name)

    active = product_filters.get("active", "")
    if active != "":
        products = products.filter(active=active)

    for_sale = product_filters.get("for_sale", "")
    if for_sale != "":
        products = products.filter(for_sale=for_sale)

    sub_type = product_filters.get("sub_type", "")
    if sub_type != "":
        products = products.filter(sub_type=sub_type)

    price = product_filters.get("price", "")
    if price.find("-") != -1:
        s, e = price.split("-")
        products = products.filter(price__range = (s, e))

    category = product_filters.get("category", "")
    if category != "":
        category = lfs_get_object_or_404(Category, pk=category)
        categories = [category]
        categories.extend(category.get_all_children())

        products = products.filter(categories__in = categories).distinct()

    products = products.order_by("%s%s" % (product_ordering_order, product_ordering))

    return products