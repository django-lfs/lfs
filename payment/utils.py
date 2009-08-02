# django imports
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

# lfs imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop
from lfs.criteria import utils as criteria_utils
from lfs.customer import utils as customer_utils
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import CREDIT_CARD
from lfs.payment.settings import PAYPAL

# other imports
from paypal.standard.conf import POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT

def update_to_valid_payment_method(request, customer, save=False):
    """After this method has been called the given customer has a valid
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
    for pm in PaymentMethod.objects.filter(active=True):
        if criteria_utils.is_valid(request, pm):
            result.append(pm)
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
    """Processes the payment depending on the selected payment method. Returns
    a dictionary with the success state, the next url and a optional error
    message.
    """
    payment_method = get_selected_payment_method(request)
    shop = lfs.core.utils.get_default_shop()

    if payment_method.id == PAYPAL and settings.LFS_PAYPAL_REDIRECT:
        return {
            "success" : True,
            "next-url" : "this is set within checkout.views",
        }
    elif payment_method.id == CREDIT_CARD:
        module = lfs.core.utils.import_module(settings.LFS_CREDIT_CARD_MODULE)
        return module.process(request)
    return {
        "success" : True,
        "next-url" : reverse("lfs_thank_you"),
    }

def create_paypal_link_for_order(order):
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
        "item_name" : shop.shop_owner,
        "amount" : order.price - float("%.2f" % order.tax),
        "tax" : "%.2f" % order.tax,
    }
    
    parameters = "&".join(["%s=%s" % (k, v) for (k, v) in info.items()])
    if settings.DEBUG:
        url = SANDBOX_POSTBACK_ENDPOINT + "?" + parameters
    else:
        url = POSTBACK_ENDPOINT + "?" + parameters

    return url
    
def create_paypal_link_for_request(request):
    """Creates paypal link for given request.
    """
    shop = lfs_get_object_or_404(Shop, pk=1)
    current_site = Site.objects.get(id=settings.SITE_ID)

    customer = lfs.customer.utils.get_customer(request)
    invoice_address = customer.selected_invoice_address

    cart = lfs.cart.utils.get_cart(request)
    cart_price, cart_tax = lfs.cart.utils.get_cart_costs()

    info = {
        "cmd" : "_xclick",
        "upload" : "1",
        "business" : settings.PAYPAL_RECEIVER_EMAIL,
        "currency_code" : shop.default_currency,
        "notify_url" : "http://" + current_site.domain + reverse('paypal-ipn'),
        "return" : "http://" + current_site.domain + reverse('paypal-pdt'),
        "first_name" : invoice_address.firstname,
        "last_name" : invoice_address.lastname,
        "address1" : invoice_address.street,
        "address2" : "",
        "city" : invoice_address.city,
        "state" : invoice_address.state,
        "zip" : invoice_address.zip_code,
        "no_shipping" : "1",
        "custom": cart.id,
        "invoice": cart.id,
        "item_name" : shop.shop_owner,
        "amount" : "%.2f" % (cart_price - cart_tax),
        "tax" : "%.2f" % cart_tax,
    }

    parameters = "&".join(["%s=%s" % (k, v) for (k, v) in info.items()])
    if settings.DEBUG:
        url = SANDBOX_POSTBACK_ENDPOINT + "?" + parameters
    else:
        url = POSTBACK_ENDPOINT + "?" + parameters

    return url