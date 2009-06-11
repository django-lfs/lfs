# django imports
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop
from lfs.criteria import utils as criteria_utils
from lfs.customer import utils as customer_utils
from lfs.order.models import Order
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import DIRECT_DEBIT
from lfs.payment.settings import CASH_ON_DELIVERY
from lfs.payment.settings import PAYPAL

# other imports
from paypal.standard.conf import POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT

def update_to_valid_payment_method(request, customer, save=False):
    """After this method has been called the current customer has a valid
    payment method.
    """
    valid_sms = get_valid_payment_methods(request)
    
    if customer.selected_payment_method not in valid_sms:
        customer.selected_payment_method = get_default_payment_method(request)
        if save:
            customer.save()

def get_valid_payment_methods(request):
    """Returns all valid payment methods (aka. selectable) for given request as
    list.
    """
    result = []
    for sm in PaymentMethod.objects.filter(active=True):
        if criteria_utils.is_valid(request, sm):
            result.append({
                "id" : sm.id,
                "name" : sm.name,
                "price" : 0.0
            })
    return result
    
def get_default_payment_method(request):
    """Returns the default payment method for given request.
    """
    active_payment_methods = PaymentMethod.objects.filter(active=True)
    return criteria_utils.get_first_valid(request, active_payment_methods)
    
def get_selected_payment_method(request):
    """Returns the selected payment method for given request. This could either 
    be an explicitly selected payment method of the current user or the default
    payment method.
    """
    customer = customer_utils.get_customer(request)
    if customer and customer.selected_payment_method:
        return customer.selected_payment_method
    else:
        return get_default_payment_method(request)

def get_payment_costs(request, payment_method):
    """Returns the payment price and tax for the given request.
    """
    if payment_method is None:
        return {
            "price" : 0.0,
            "tax" : 0.0            
        }

    try:
        tax_rate = payment_method.tax.rate
    except AttributeError:
        tax_rate = 0.0

    price = criteria_utils.get_first_valid(request, 
        payment_method.prices.all())
    
    if price is None:
        price = payment_method.price
        tax = (tax_rate/(tax_rate+100)) * price

        return {
            "price" : price,
            "tax" : tax
        }
    else:
        tax = (tax_rate/(tax_rate+100)) * price.price

        return {
            "price" : price.price,
            "tax" : tax
        }        

def process_payment(request):
    """Processes the payment depending on the selected payment method. 
    
    Returns a dictionary with the success state and a next url. 
    """
    # TODO: Check dependencies
    from lfs.order import utils as order_utils
    payment_method = get_selected_payment_method(request)
    #import ipdb; ipdb.set_trace()
    shop = lfs_get_object_or_404(Shop, pk=1)

    order = order_utils.add_order(request)
    if order is None:
        url = reverse("lfs_cart")
    else:
        if payment_method.id == PAYPAL and settings.LFS_PAYPAL_REDIRECT and order is not None:
            url = create_paypal_link(order)
        else:
            url = reverse("lfs_thank_you")
            
    return {
        "success" : True,
        "next-url" : url,
    }
    
def create_paypal_link(order):
    """Creates paypal link for given order.
    """    
    shop = lfs_get_object_or_404(Shop, pk=1)
    current_site = Site.objects.get(id=settings.SITE_ID)
    
    info = {
        "cmd" : "_xclick",
        "upload" : "1",
        "business" : settings.PAYPAL_RECEIVER_EMAIL,
        "currency_code" : shop.default_currency,
        "notify_url" : "http://" + current_site.domain + reverse('paypal-ipn'),
        "return" : "http://" + current_site.domain + reverse('paypal-pdt'),
        "first_name" : order.invoice_firstname,
        "last_name" : order.invoice_lastname,
        "address1" : order.invoice_street,
        "address2" : "",
        "city" : order.invoice_city,
        "state" : order.invoice_state,
        "zip" : order.invoice_zip_code,
        "no_shipping" : "1",
        "custom": order.uuid,
        "invoice": order.uuid,
        "item_name" : order.get_name(),
        "amount" : order.price - float("%.2f" % order.tax),
        "tax" : "%.2f" % order.tax,
    }
    
    parameters = "&".join(["%s=%s" % (k, v) for (k, v) in info.items()])
    if settings.DEBUG:
        url = SANDBOX_POSTBACK_ENDPOINT + "?" + parameters
    else:
        url = POSTBACK_ENDPOINT + "?" + parameters
    
    return url