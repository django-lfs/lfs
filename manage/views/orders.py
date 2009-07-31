# python imports
from datetime import datetime
from datetime import timedelta

# django imports
from django.db.models import Q
from django.contrib.auth.decorators import permission_required
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.core.utils
import lfs.order.settings
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder
from lfs.mail import utils as mail_utils
from lfs.order.models import Order

@permission_required("manage_shop", login_url="/login/")
def manage_orders(request, template_name="manage/order/manage_orders.html"):
    """Dispatches to the first order or the order overview.
    """
    try:
        order = Order.objects.all()[0]
    except:
        return HttpResponseRedirect(reverse("lfs_orders"))
    else:
        return HttpResponseRedirect(
            reverse("lfs_manage_order", kwargs={"order_id" : order.id}))

@permission_required("manage_shop", login_url="/login/")
def orders_view(request, template_name="manage/order/orders.html"):
    """Main view to display an order overview.
    """
    return render_to_response(template_name, RequestContext(request, {
        "orders_inline" : orders_inline(request, as_string=True),
    }))

def orders_inline(request, as_string=False, template_name="manage/order/orders_inline.html"):
    """Displays the orders. This is factored out in order to reload it via
    ajax request.
    """
    orders = Order.objects.all()

    order_filters = request.session.get("order-filters", {})

    # name
    name = order_filters.get("name", "")
    if name != "":
        f  = Q(customer_lastname__icontains=name)
        f |= Q(customer_firstname__icontains=name)
        orders = orders.filter(f)

    # state
    state_id = order_filters.get("state")
    if state_id is not None:
        orders = orders.filter(state=state_id)

    # start
    start = order_filters.get("start", "")
    if start != "":
        s = lfs.core.utils.get_start_day(start)
    else:
        s = datetime.min

    # end
    end = order_filters.get("end", "")
    if end != "":
        e = lfs.core.utils.get_end_day(end)
    else:
        e = datetime.max

    orders = orders.filter(created__range=(s, e))

    try:
        amount = int(request.REQUEST.get("amount", 20))
    except TypeError:
        amount = 20

    page = request.REQUEST.get("page", 1)
    paginator = Paginator(orders, amount)
    page = paginator.page(page)

    states = []
    for state in lfs.order.settings.ORDER_STATES:
        states.append({
            "id"   : state[0],
            "name" : state[1],
            "selected" : state_id == str(state[0]),
        })

    result = render_to_string(template_name, RequestContext(request, {
        "paginator" : paginator,
        "page" : page,
        "states" : states,
        "start" : start,
        "end" : end,
        "name" : name,
    }))
    
    if as_string:
        return result
    else:
        html = (("#orders-inline", result),)

        result = simplejson.dumps({
            "html" : html,
        }, cls = LazyEncoder)

        return HttpResponse(result)

def set_order_filters(request):
    """Sets order filters given by passed request.
    """
    order_filters = request.session.get("order-filters", {})

    if request.POST.get("name", "") != "":
        order_filters["name"] = request.POST.get("name")
    else:
        if order_filters.get("name"):
            del order_filters["name"]

    if request.POST.get("start", "") != "":
        order_filters["start"] = request.POST.get("start")
    else:
        if order_filters.get("start"):
            del order_filters["start"]

    if request.POST.get("end", "") != "":
        order_filters["end"] = request.POST.get("end")
    else:
        if order_filters.get("end"):
            del order_filters["end"]

    if request.POST.get("state", "") != "":
        order_filters["state"] = request.POST.get("state")
    else:
        if order_filters.get("state"):
            del order_filters["state"]

    request.session["order-filters"] = order_filters

    html = (("#orders-inline", orders_inline(request, as_string=True)),)
    msg = _(u"Filters has been set")

    result = simplejson.dumps({
        "html" : html,
        "message" : msg,
    }, cls = LazyEncoder)

    return HttpResponse(result)

def set_order_filters_date(request):
    """Sets the date filter by given short cut link
    """
    order_filters = request.session.get("order-filters", {})

    start = datetime.now() - timedelta(int(request.REQUEST.get("start")))
    end = datetime.now() - timedelta(int(request.REQUEST.get("end")))

    order_filters["start"] = start.strftime("%Y-%m-%d")
    order_filters["end"] = end.strftime("%Y-%m-%d")
    request.session["order-filters"] = order_filters

    html = (("#orders-inline", orders_inline(request, as_string=True)),)
    msg = _(u"Filters has been set")

    result = simplejson.dumps({
        "html" : html,
        "message" : msg,
    }, cls = LazyEncoder)

    return HttpResponse(result)

def reset_order_filters(request):
    """resets order filter.
    """
    if request.session.has_key("order-filters"):
        del request.session["order-filters"]

    html = (("#orders-inline", orders_inline(request, as_string=True)),)
    msg = _(u"Filters has been reset")

    result = simplejson.dumps({
        "html" : html,
        "message" : msg,
    }, cls = LazyEncoder)

    return HttpResponse(result)

@permission_required("manage_shop", login_url="/login/")
def order_view(request, order_id, template_name="manage/order/order.html"):
    """Displays order with provided order id.
    """
    order = lfs_get_object_or_404(Order, pk=order_id)
    orders = Order.objects.all()

    return render_to_response(template_name, RequestContext(request, {
        "current_order" : order,
        "selectable_orders" : selectable_orders_inline(request, as_string=True),
    }))

@permission_required("manage_shop", login_url="/login/")
def selectable_orders_inline(request, as_string=False,
    template_name="manage/order/selectable_orders_inline.html"):
    """Displays the selectable orders for the order view. (Used to switch
    quickly from one order to another.)
    """
    orders = Order.objects.all()
    paginator = Paginator(orders, 20)

    try:
        page = int(request.REQUEST.get("page", 1))
    except TypeError:
        page = 1
    page = paginator.page(page)

    result = render_to_string(template_name, RequestContext(request, {
        "orders" : orders,
        "paginator" : paginator,
        "page" : page,
    }))

    if as_string:
        return result
    else:
        result = simplejson.dumps({
            "html" : (("#selectable-orders", result),),
        }, cls = LazyEncoder)

        return HttpResponse(result)

# Actions
@permission_required("manage_shop", login_url="/login/")
def delete_order(request, order_id):
    """Deletes order with provided order id.
    """
    order = lfs_get_object_or_404(Order, pk=order_id)
    order.delete()

    try:
        order = Order.objects.all()[0]
        url = reverse("lfs_manage_order", kwargs={"order_id" : order.id})
    except IndexError:
        url = reverse("lfs_manage_orders")

    return HttpResponseRedirect(url)

@permission_required("manage_shop", login_url="/login/")
def send_order(request, order_id):
    """Sends order with passed order id to the customer of this order.
    """
    order = lfs_get_object_or_404(Order, pk=order_id)
    mail_utils.send_order_received_mail(order)

    return lfs.core.utils.set_message_cookie(
        url = reverse("lfs_manage_order", kwargs={"order_id" : order.id}),
        msg = _(u"Order has been sent."),
    )