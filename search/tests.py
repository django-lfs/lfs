# django imports
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.test.client import Client

# test imports
from lfs.catalog.models import Product
from lfs.cart.models import Cart
from lfs.cart.models import CartItem
from lfs.cart.views import add_to_cart
from lfs.cart import utils as cart_utils
from lfs.customer.models import Address
from lfs.customer.models import Customer
from lfs.order.utils import add_order
from lfs.order.settings import SUBMITTED
from lfs.payment.models import PaymentMethod
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax
from lfs.tests.utils import DummyRequest

class SearchTestCase(TestCase):
    """Unit tests for lfs.search
    """
    def setUp(self):
        """
        """
        self.p1 = Product.objects.create(name="Product 1", slug="p1", price=9)
        self.p2 = Product.objects.create(name="Product 2", slug="p2", price=11)

    def test_search(self):
        """
        """
        response = self.client.get("/shops/product/p1")
        self.failUnless(response.content.find("Product 1") != -1)
        