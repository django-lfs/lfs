# django imports
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response
from django.template import RequestContext

# lfs imports
import lfs.cart.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.cart.models import Cart

@permission_required("manage_shop", login_url="/login/")
def carts_view(request, template_name="manage/cart/carts.html"):
    """Displays all orders.
    """
    carts = []
    for cart in Cart.objects.all():
        carts.append({
            "id" : cart.id,
            "amount_of_items" : cart.amount_of_items,
            "creation_date" : cart.creation_date,
        })

    return render_to_response(template_name, RequestContext(request, {
        "carts" : carts,
    }))

@permission_required("manage_shop", login_url="/login/")
def cart_view(request, cart_id, template_name="manage/cart/cart.html"):
    """Displays cart with provided cart id.
    """
    cart = lfs_get_object_or_404(Cart, pk=cart_id)
    carts = Cart.objects.all()

    return render_to_response(template_name, RequestContext(request, {
        "current_cart" : cart,
        "carts" : carts,
    }))
