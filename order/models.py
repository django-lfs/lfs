# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.core.models import Country
from lfs.catalog.models import Product
from lfs.order.settings import ORDER_STATES
from lfs.order.settings import SUBMITTED
from lfs.shipping.models import ShippingMethod
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import PAYPAL
import lfs.payment.utils
        
class Order(models.Model):
    """An order is created when products has been sold.
    """
    created = models.DateTimeField(_(u"Created"), auto_now_add=True)
    state = models.PositiveSmallIntegerField(_(u"State"), choices=ORDER_STATES, default=SUBMITTED)

    price = models.FloatField(_(u"Price"), default=0.0)
    tax = models.FloatField(_(u"Tax"), default=0.0)
    
    customer_firstname = models.CharField(_(u"firstname"), max_length=50)
    customer_lastname = models.CharField(_(u"lastname"), max_length=50)
    customer_email = models.CharField(_(u"lastname"), max_length=50)

    invoice_firstname = models.CharField(_(u"Invoice firstname"), max_length=50)
    invoice_lastname = models.CharField(_(u"Invoice lastname"), max_length=50)    
    invoice_street = models.CharField(_(u"Invoice street"), blank=True, max_length=100)
    invoice_zip_code = models.CharField(_(u"Invoice zip code"), max_length=10)    
    invoice_city = models.CharField(_(u"Invoice city"), max_length=50)
    invoice_country = models.ForeignKey(Country, related_name="orders_invoice_country")
    invoice_phone = models.CharField(_(u"Invoice phone"), blank=True, max_length=20)
    invoice_email = models.EmailField(_(u"Invoice e-mail"), blank=True, null=True, max_length=50)

    shipping_firstname = models.CharField(_(u"Shipping firstname"), max_length=50)
    shipping_lastname = models.CharField(_(u"Shipping lastname"), max_length=50)    
    shipping_street = models.CharField(_(u"Shipping street"), blank=True, max_length=100)
    shipping_zip_code = models.CharField(_(u"Shipping zip code"), max_length=10)    
    shipping_city = models.CharField(_(u"Shipping city"), max_length=50)
    shipping_country = models.ForeignKey(Country, related_name="orders_shipping_country")
    shipping_phone = models.CharField(_(u"Shipping phone"), blank=True, max_length=20)
    shipping_email = models.EmailField(_(u"Shipping e-mail"), blank=True, null=True, max_length=50)
    
    shipping_method = models.ForeignKey(ShippingMethod, verbose_name=_(u"Shipping Method"), blank=True, null=True)
    shipping_price = models.FloatField(_(u"Shipping Price"), default=0.0)
    shipping_tax = models.FloatField(_(u"Shipping Tax"), default=0.0)

    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_(u"Payment Method"), blank=True, null=True)
    payment_price = models.FloatField(_(u"Payment Price"), default=0.0)
    payment_tax = models.FloatField(_(u"Payment Tax"), default=0.0)

    account_number = models.CharField(_(u"Account number"), blank=True, max_length=30)
    bank_identification_code = models.CharField(_(u"Bank identication code"), blank=True, max_length=30)
    bank_name = models.CharField(_(u"Bank name"), blank=True, max_length=100)
    depositor = models.CharField(_(u"Depositor"), blank=True, max_length=100)
    
    message = models.TextField(_(u"Message"), blank=True)
    
    class Meta:
        ordering = ("-created", )
     
    def get_pay_link(self):
        """Returns a pay link for the selected payment method
        """
        if self.payment_method.id == PAYPAL:
            pay_link = lfs.payment.utils.create_paypal_link(self)
        else:
            pay_link = None
            
        return pay_link
        
class OrderItem(models.Model):
    """An order items holds the sold product, its amount and some other relevant 
    product values like the price at the time the product has been sold.
    """
    order = models.ForeignKey(Order, related_name="items")

    price_net = models.FloatField(_(u"Price net"), default=0.0)
    price_gross = models.FloatField(_(u"Price gross"), default=0.0)
    tax = models.FloatField(_(u"Tax"), default=0.0)
    
    # A optional reference to the origin product. This is optional in case the 
    # product has been deleted. TODO: Decide: Are products able to be delete?
    product = models.ForeignKey(Product, blank=True, null=True)
    
    # Values of the product at the time the orders has been created
    product_amount = models.IntegerField(_(u"Product quantity"), blank=True, null=True)
    product_sku = models.CharField(_(u"Product SKU"), blank=True, max_length=100)
    product_name = models.CharField(_(u"Product name"), blank=True, max_length=100)
    product_price_net = models.FloatField(_(u"Product price net"), default=0.0)
    product_price_gross = models.FloatField(_(u"Product price gross"), default=0.0)
    product_tax = models.FloatField(_(u"Product tax"), default=0.0)