# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

# lfs imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
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
    """Displays all orders.
    """
    orders = Order.objects.all()
    return render_to_response(template_name, RequestContext(request, {
        "orders" : orders
    }))    

@permission_required("manage_shop", login_url="/login/")    
def order_view(request, order_id, template_name="manage/order/order.html"):
    """Displays order with provided order id.
    """ 
    order = lfs_get_object_or_404(Order, pk=order_id)
    orders = Order.objects.all()
    
    return render_to_response(template_name, RequestContext(request, {
        "current_order" : order,
        "orders" : orders,
    }))
    
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