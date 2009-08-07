# python imports
from datetime import datetime
from datetime import timedelta

# django imports
from django.db.models import Q
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.cart.utils
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.cart.models import Cart
from lfs.core.utils import LazyEncoder
from lfs.customer.models import Customer
from lfs.order.models import Order

@permission_required("manage_shop", login_url="/login/")
def customer(request, customer_id, template_name="manage/customer/customer.html"):
    """Displays customer with provided customer id.
    """
    return render_to_response(template_name, RequestContext(request, {
        "customer_inline" : customer_inline(request, customer_id, as_string=True),
        "selectable_customers_inline" : selectable_customers_inline(request, customer_id, as_string=True),
    }));

def customer_inline(request, customer_id, as_string=False, template_name="manage/customer/customer_inline.html"):
    """Displays customer with provided customer id.
    """
    customer_filters = request.session.get("customer-filters", {})    
    customer = lfs_get_object_or_404(Customer, pk=customer_id)
    orders = Order.objects.filter(session=customer.session)

    try:
        cart = Cart.objects.get(session=customer.session)
        cart_price = lfs.cart.utils.get_cart_price(request, cart, total=True)
    except Cart.DoesNotExist:
        cart = None
        cart_price = None

    result = render_to_string(template_name, RequestContext(request, {
        "customer" : customer,
        "orders" : orders,
        "cart" : cart,
        "cart_price" : cart_price,
        "name" : customer_filters.get("name", ""), 
    }))

    if as_string:
        return result
    else:
        html = (("#customer-inline", result),)

        result = simplejson.dumps({
            "html" : html,
        }, cls = LazyEncoder)

        return HttpResponse(result)

@permission_required("manage_shop", login_url="/login/")
def customers(request, template_name="manage/customer/customers.html"):
    """Base view to display customers overview.
    """
    return render_to_response(template_name, RequestContext(request, {
        "customers_inline" : customers_inline(request, as_string=True),
    }))

@permission_required("manage_shop", login_url="/login/")
def customers_inline(request, as_string=False, template_name="manage/customer/customers_inline.html"):
    """Displays carts overview.
    """
    customer_filters = request.session.get("customer-filters", {})
    temp = _get_filtered_customers(customer_filters)

    paginator = Paginator(temp, 30)

    page = request.REQUEST.get("page", 1)
    page = paginator.page(page)
    
    customers = []
    for customer in page.object_list:
        try:
            cart = Cart.objects.get(session=customer.session)
            cart_price = lfs.cart.utils.get_cart_price(request, cart, total=True)
        except Cart.DoesNotExist:
            cart_price = None

        orders = Order.objects.filter(session=customer.session)         
        customers.append({
            "customer" : customer,
            "orders" : len(orders),
            "cart_price" : cart_price,
        })
        
    result = render_to_string(template_name, RequestContext(request, {
        "customers" : customers,
        "page" : page,
        "paginator" : paginator,
        "start" : customer_filters.get("start", ""),
        "end" : customer_filters.get("end", ""),
    }))

    if as_string:
        return result
    else:
        html = (("#customers-inline", result),)

        result = simplejson.dumps({
            "html" : html,
        }, cls = LazyEncoder)

        return HttpResponse(result)

def selectable_customers_inline(request, customer_id=0, as_string=False,
    template_name="manage/customer/selectable_customers_inline.html"):
    """Display selectable customers.
    """
    customer_filters = request.session.get("customer-filters", {})
    customers = _get_filtered_customers(customer_filters)

    paginator = Paginator(customers, 30)

    try:
        page = int(request.REQUEST.get("page", 1))
    except TypeError:
        page = 1
    page = paginator.page(page)

    result = render_to_string(template_name, RequestContext(request, {
        "paginator" : paginator,
        "page" : page,
        "customer_id" : int(customer_id),
    }))

    if as_string:
        return result
    else:
        result = simplejson.dumps({
            "html" : (("#selectable-customers-inline", result),),
        }, cls = LazyEncoder)

        return HttpResponse(result)

def set_customer_filters(request):
    """Sets customer filters given by passed request.
    """
    customer_filters = request.session.get("customer-filters", {})

    if request.POST.get("name", "") != "":
        customer_filters["name"] = request.POST.get("name")
    else:
        if customer_filters.get("name"):
            del customer_filters["name"]

    request.session["customer-filters"] = customer_filters
    
    if request.REQUEST.get("came-from") == "customer":
        customer_id = request.REQUEST.get("customer-id")
        html = (
            ("#selectable-customers-inline", selectable_customers_inline(request, as_string=True)),
            ("#customer-inline", customer_inline(request, customer_id=customer_id, as_string=True)),
        )
    else:
        html = (("#customers-inline", customers_inline(request, as_string=True)),)

    msg = _(u"Customer filters has been set")

    result = simplejson.dumps({
        "html" : html,
        "message" : msg,
    }, cls = LazyEncoder)

    return HttpResponse(result)

def reset_customer_filters(request):
    """Resets all customer filters.
    """
    if request.session.has_key("customer-filters"):
        del request.session["customer-filters"]

    if request.REQUEST.get("came-from") == "customer":
        customer_id = request.REQUEST.get("customer-id")
        html = (
            ("#selectable-customers-inline", selectable_customers_inline(request, as_string=True)),
            ("#customer-inline", customer_inline(request, customer_id=customer_id, as_string=True)),
        )
    else:
        html = (("#customers-inline", customers_inline(request, as_string=True)),)

    msg = _(u"Customer filters has been reset")

    result = simplejson.dumps({
        "html" : html,
        "message" : msg,
    }, cls = LazyEncoder)

    return HttpResponse(result)

def _get_filtered_customers(customer_filters):
    """
    """
    customers = Customer.objects.exclude(selected_invoice_address=None)

    # name
    name = customer_filters.get("name", "")
    
    if name != "":
        f  = Q(selected_invoice_address__lastname__icontains=name)
        f |= Q(selected_invoice_address__firstname__icontains=name)
        customers = customers.filter(f)
    
    return customers