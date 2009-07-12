# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
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

    try:
        start = int(request.GET.get("start", 0))
    except ValueError:
        start = 0

    try:
        amount = int(request.GET.get("amount", 10))
    except ValueError:
        amount = 0

    end = start + amount
        
    carts = []
    for cart in Cart.objects.all().order_by("-creation_date")[start:end]:

        products = []
        total = 0
        for item in cart.items():
            total += item.get_price_gross()
            products.append(item.product.get_name)

        if cart.user:
            if cart.user.first_name:
                user_name = cart.user.first_name + " "
            if cart.user.last_name:
                user_name += cart.user.last_name
        else:
            user_name = None

        carts.append({
            "id" : cart.id,
            "amount_of_items" : cart.amount_of_items,
            "session" : cart.session,
            "user" : cart.user,
            "total" : total,
            "products" : ", ".join(products),
            "creation_date" : cart.creation_date,
            "user_name" : user_name,
        })
    
    if start == 0:
        previous_url = None
    elif (start - amount) < 0:
        previous_url = reverse("lfs_manage_carts") + "?start=0"
    else:
        previous_url = reverse("lfs_manage_carts") + "?start=%s" % (start - amount)

    if (start > len(Cart.objects.all())):
        next_url = None
    else:
        next_url = reverse("lfs_manage_carts") + "?start=%s" % end
    
    if previous_url and amount:
        previous_url += "&amount=%s" % amount
    if next_url and amount:
        next_url += "&amount=%s" % amount
        
    return render_to_response(template_name, RequestContext(request, {
        "carts" : carts,
        "previous_url" : previous_url,
        "next_url" : next_url,
    }))

@permission_required("manage_shop", login_url="/login/")
def cart_view(request, cart_id, template_name="manage/cart/cart.html"):
    """Displays cart with provided cart id.
    """
    cart = lfs_get_object_or_404(Cart, pk=cart_id)
    carts = Cart.objects.all().order_by("-creation_date")

    total = 0
    for item in cart.items():
        total += item.get_price_gross()

    if cart.user:
        if cart.user.first_name:
            user_name = cart.user.first_name + " "
        if cart.user.last_name:
            user_name += cart.user.last_name
    else:
        user_name = None

    return render_to_response(template_name, RequestContext(request, {
        "cart" : cart,
        "user_name" : user_name,
        "carts" : carts,
        "total" : total,

    }))
