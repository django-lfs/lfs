# django imports
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson

# lfs imports
from lfs.cart import utils as cart_utils
from lfs.checkout.forms import OnePageCheckoutForm
from lfs.customer import utils as customer_utils
from lfs.customer.models import Address
from lfs.customer.models import BankAccount
from lfs.shipping import utils as shipping_utils
from lfs.payment import utils as payment_utils

def checkout(request):
    """Dispatcher to display the correct checkout form
    """
    cart = cart_utils.get_cart(request)

    if cart is None or not cart.items():
        return empty_page_checkout(request)
        
    return one_page_checkout(request)

def cart_inline(request, template_name="checkout/checkout_cart_inline.html"):
    """Displays the cart items of the checkout page.

    Factored out to be reusable for the starting request (which renders the
    whole checkout page and subsequent ajax requests which refresh the 
    cart items.
    """
    cart = cart_utils.get_cart(request)
    
    # Shipping
    selected_shipping_method = shipping_utils.get_selected_shipping_method(request)
    shipping_costs = shipping_utils.get_shipping_costs(request, selected_shipping_method)    
    
    # Payment
    selected_payment_method = payment_utils.get_selected_payment_method(request)
    payment_costs = payment_utils.get_payment_costs(request, selected_payment_method)
    
    # cart costs
    cart_costs = cart_utils.get_cart_costs(request, cart)    
    cart_price = cart_costs["price"] + shipping_costs["price"] + payment_costs["price"]
    cart_tax = cart_costs["tax"] + shipping_costs["tax"] + payment_costs["tax"]
        
    return render_to_string(template_name, RequestContext(request, {
        "cart" : cart,
        "cart_price" : cart_price,
        "cart_tax" : cart_tax,
        "shipping_price" : shipping_costs["price"],
        "payment_price" : payment_costs["price"],        
        "selected_shipping_method" : selected_shipping_method,
        "selected_payment_method" : selected_payment_method,
    }))
    
def one_page_checkout(request, template_name="checkout/one_page_checkout.html"):
    """One page checkout form
    """
    customer = customer_utils.get_or_create_customer(request)
    if request.method == "POST":
        form = OnePageCheckoutForm(request.POST)
        if form.is_valid():            
            # Create or update shipping address
            if customer.selected_shipping_address is None:
                shipping_address = Address.objects.create(
                    firstname = form.cleaned_data.get("shipping_firstname"),
                    lastname = form.cleaned_data.get("shipping_lastname"),
                    street = form.cleaned_data.get("shipping_street"),
                    zip_code = form.cleaned_data.get("shipping_zip_code"),
                    city = form.cleaned_data.get("shipping_city"),
                    country_id = form.cleaned_data.get("shipping_country"),
                    phone = form.cleaned_data.get("shipping_phone"),
                    email = form.cleaned_data.get("shipping_email"),
                )
                customer.selected_shipping_address = shipping_address
            else:
                selected_shipping_address = customer.selected_shipping_address
                selected_shipping_address.firstname = form.cleaned_data.get("shipping_firstname")
                selected_shipping_address.lastname = form.cleaned_data.get("shipping_lastname")
                selected_shipping_address.street = form.cleaned_data.get("shipping_street")
                selected_shipping_address.zip_code = form.cleaned_data.get("shipping_zip_code")
                selected_shipping_address.city = form.cleaned_data.get("shipping_city")
                selected_shipping_address.country_id = form.cleaned_data.get("shipping_country")
                selected_shipping_address.phone = form.cleaned_data.get("shipping_phone")
                selected_shipping_address.email = form.cleaned_data.get("shipping_email")
                selected_shipping_address.save()
                        
            if form.cleaned_data.get("no_invoice"):
                if customer.selected_invoice_address is None:
                    customer.selected_invoice_address = shipping_address
                else:
                    selected_invoice_address = customer.selected_invoice_address
                    selected_invoice_address.firstname = form.cleaned_data.get("shipping_firstname")
                    selected_invoice_address.lastname = form.cleaned_data.get("shipping_lastname")
                    selected_invoice_address.street = form.cleaned_data.get("shipping_street")
                    selected_invoice_address.zip_code = form.cleaned_data.get("shipping_zip_code")
                    selected_invoice_address.city = form.cleaned_data.get("shipping_city")
                    selected_invoice_address.country_id = form.cleaned_data.get("shipping_country")
                    selected_invoice_address.phone = form.cleaned_data.get("shipping_phone")
                    selected_invoice_address.save()
            else:    
                # Create or update invoice address
                if customer.selected_invoice_address is None:
                    invoice_address = Address.objects.create(
                        firstname = form.cleaned_data.get("invoice_firstname"),
                        lastname = form.cleaned_data.get("invoice_lastname"),
                        street = form.cleaned_data.get("invoice_street"),
                        zip_code = form.cleaned_data.get("invoice_zip_code"),
                        city = form.cleaned_data.get("invoice_city"),
                        country_id = form.cleaned_data.get("invoice_country"),
                        phone = form.cleaned_data.get("invoice_phone"),
                        email = form.cleaned_data.get("invoice_email"),
                    )
                    customer.selected_invoice_address = invoice_address
                else:
                    selected_invoice_address = customer.selected_invoice_address
                    selected_invoice_address.firstname = form.cleaned_data.get("invoice_firstname")
                    selected_invoice_address.lastname = form.cleaned_data.get("invoice_lastname")
                    selected_invoice_address.street = form.cleaned_data.get("invoice_street")
                    selected_invoice_address.zip_code = form.cleaned_data.get("invoice_zip_code")
                    selected_invoice_address.city = form.cleaned_data.get("invoice_city")
                    selected_invoice_address.country_id = form.cleaned_data.get("invoice_country")
                    selected_invoice_address.phone = form.cleaned_data.get("invoice_phone")
                    selected_invoice_address.save()
            
            # 1 = Direct Debit
            if form.data.get("payment-method") == "1":
                bank_account = BankAccount.objects.create(
                    account_number = form.cleaned_data.get("account_number"),
                    bank_identification_code = form.cleaned_data.get("bank_identification_code"),
                    bank_name = form.cleaned_data.get("bank_name"),
                    depositor = form.cleaned_data.get("depositor"),
                )
                
                customer.selected_bank_account = bank_account

            # Save the selected information to the customer
            customer.save()
            
            # process the payment method ...
            result =  payment_utils.process_payment(request)
            
            # and redirect the next url. This could be a payment method relevant (e.g.
            # in case of PayPal or the the thank-you page.)
            if result.get("success"):
                return HttpResponseRedirect(result.get("next-url"))
            else:
                raise NotImplementedError
    else:
        initial = {}
        if customer.selected_invoice_address is not None:
            shipping_address = customer.selected_shipping_address
            initial.update({
                "shipping_firstname" : shipping_address.firstname,
                "shipping_lastname" : shipping_address.lastname,
                "shipping_street" : shipping_address.street,
                "shipping_zip_code" : shipping_address.zip_code,
                "shipping_city" : shipping_address.city,
                "shipping_phone" : shipping_address.phone,
                "shipping_email" : shipping_address.email,
            })
            invoice_address = customer.selected_invoice_address
            initial.update({
                "invoice_firstname" : invoice_address.firstname,
                "invoice_lastname" : invoice_address.lastname,
                "invoice_street" : invoice_address.street,
                "invoice_zip_code" : invoice_address.zip_code,
                "invoice_city" : invoice_address.city,
                "invoice_country" : invoice_address.country_id,
                "invoice_phone" : invoice_address.phone,
                "invoice_email" : invoice_address.email,
            })
            
        # Set the addresses country to the current selected in any case.
        country = shipping_utils.get_selected_shipping_country(request)
        initial["shipping_country"] = country.id
        initial["invoice_country"] = country.id
        form = OnePageCheckoutForm(initial=initial)

    cart = cart_utils.get_cart(request)
    
    # Payment
    selected_payment_method = payment_utils.get_selected_payment_method(request)
    
    return render_to_response(template_name, RequestContext(request, {
        "form" : form,
        "cart_inline" : cart_inline(request),
        "shipping_inline" : shipping_inline(request),
        "payment_methods" : payment_utils.get_valid_payment_methods(request),        
        "selected_payment_method" : selected_payment_method,        
    }))

def empty_page_checkout(request, template_name="checkout/empty_page_checkout.html"):
    """
    """    
    return render_to_response(template_name, RequestContext(request, {
        "shopping_url" : reverse("lfs.core.views.shop_view"),
    }))
    
def thank_you(request, template_name="checkout/thank_you_page.html"):
    """Displays a thank you page ot the customer
    """
    order = request.session.get("order")        
    return render_to_response(template_name, RequestContext(request, {
        "order" : order,
    }))

def shipping_inline(request, template_name="checkout/shipping_inline.html"):
    """Displays the selectable shipping methods of the checkout page.
    
    Factored out to be reusable for the starting request (which renders the
    whole checkout page and subsequent ajax requests which refresh the
    selectable shipping methods.
    """
    selected_shipping_method = shipping_utils.get_selected_shipping_method(request)
    shipping_methods = shipping_utils.get_valid_shipping_methods(request)

    return render_to_string(template_name, RequestContext(request, {
        "shipping_methods" : shipping_methods,
        "selected_shipping_method" : selected_shipping_method,
    }))

def changed_checkout(request):
    """
    """
    customer = customer_utils.get_or_create_customer(request)
    _save_customer(request, customer)

    result = simplejson.dumps({
        "cart" : cart_inline(request),
    })
    
    return HttpResponse(result)

def changed_country(request):
    """Updates and saves the customer after the country has been chagend and
    updates the involved parts of the checkout page.
    """
    customer = customer_utils.get_or_create_customer(request)
    _save_country(request, customer)
    
    cart = cart_inline(request)
    shipping = shipping_inline(request)
    
    result = simplejson.dumps({
        "cart" : cart,
        "shipping" : shipping
    })
    
    return HttpResponse(result)

def _save_country(request, customer):
    """
    """
    # Update shipping country
    country = request.POST.get("shipping_country")
    if customer.selected_shipping_address:
        customer.selected_shipping_address.country_id = country
        customer.selected_shipping_address.save()
    customer.selected_country_id = country
    customer.save()
    
    shipping_utils.update_to_valid_shipping_method(request, customer)
    payment_utils.update_to_valid_payment_method(request, customer)
    customer.save()
    
def _save_customer(request, customer):
    """
    """
    shipping_method = request.POST.get("shipping-method")    
    customer.selected_shipping_method_id = shipping_method
    customer.save()
    
    payment_method = request.POST.get("payment-method")
    customer.selected_payment_method_id = payment_method
    customer.save()
