# django imports
from django import forms
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.catalog.models import Product

class Cart(models.Model):
    """A cart is a container for products which are supposed to be bought by a 
    shop customer.
    
    Instance variables:
    
    - user
       The user to which the cart belongs to
    - session
       The session to which the cart belongs to

    A cart can be assigned either to the current logged in User (in case 
    the shop user is logged in) or to the current session (in case the shop user 
    is not logged in).

    A cart is only created if it needs to. When the shop user adds something to 
    the cart.
    """     
    user = models.ForeignKey(User, verbose_name=_(u"User"), blank=True, null=True)
    session = models.CharField(_(u"Session"), blank=True, max_length=100)
    
    def items(self):
        """Returns the items of the cart.
        """
        cache_key = "cart-items-%s" % self.id
        items = cache.get(cache_key)
        if items is None:
            items = CartItem.objects.filter(cart=self)
            cache.set(cache_key, items)
        return items
    
    @property
    def amount_of_items(self):
        """Returns the amount of items of the cart.
        """
        amount = 0
        for item in self.items():
            amount += item.amount
        return amount

class CartItem(models.Model):    
    """A cart item belongs to a cart. It stores the product and the amount of 
    the product which has been taken into the cart.
    
    Instance variables: 
    
    - product
       A reference to a product which is supposed to be bought
    - amount
       Amount of the product which is supposed to be bought.
    """
    cart = models.ForeignKey(Cart, verbose_name=_(u"Cart"))
    product = models.ForeignKey(Product, verbose_name=_(u"Product"))
    amount = models.IntegerField(_(u"Quantity"), blank=True, null=True)
    
    class Meta:
        ordering = ['id']
    
    def get_price(self):
        """
        """
        return self.get_price_gross()
        
    def get_price_net(self):
        """Returns the total price of the cart item, which is just the
        multiplication of the product's price and the amount of the product 
        within in the cart.
        """
        return self.product.get_price_net() * self.amount

    def get_price_gross(self):
        """Returns the gross price of the product.
        """
        return self.product.get_price_gross() * self.amount

    def get_tax(self):
        """Returns the absolute tax of the product.
        """
        return self.product.get_tax() * self.amount
        
class CartPortlet(models.Model):
    """A portlet to display news.
    """
    title = models.CharField(_(u"Title"), blank=True, max_length=50)
    
    def __unicode__(self):
        return "%s" % self.id
        
    def render(self, context):
        """Renders the portlet as html.
        """         
        import lfs.cart.utils
        
        request = context.get("request")
        cart = lfs.cart.utils.get_cart(request)
        if cart is None:
            amount_of_items = None
            price = None
        else:
            amount_of_items = cart.amount_of_items
            price = lfs.cart.utils.get_cart_price(request, cart, total=True)
        
        return render_to_string("cart/cart_portlet.html", {
            "title" : self.title,
            "amount_of_items" : amount_of_items,
            "price" : price,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        })
        
    def form(self, **kwargs):
        """
        """
        return CartPortletForm(instance=self, **kwargs)
        
class CartPortletForm(forms.ModelForm):
    """
    """
    class Meta:
        model = CartPortlet