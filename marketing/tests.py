# django imports
from django.core.urlresolvers import reverse
from django.test import TestCase

# lfs import
from lfs.catalog.models import Product
from lfs.order.models import Order
from lfs.order.models import OrderItem
import lfs.marketing.utils

class UtilsTestCase(TestCase):
    """Tests the utils of the lfs.marketing.
    """
    def setUp(self):
        """
        """
        self.p1 = Product.objects.create(name="Product 1", slug="product-1")
        self.p2 = Product.objects.create(name="Product 2", slug="product-2")
        self.p3 = Product.objects.create(name="Product 3", slug="product-3")
        self.p4 = Product.objects.create(name="Product 4", slug="product-4")
        
        self.o = Order.objects.create()
        self.oi1 = OrderItem.objects.create(order=self.o, product_amount=1, product=self.p1)
        self.oi2 = OrderItem.objects.create(order=self.o, product_amount=2, product=self.p2)
        self.oi3 = OrderItem.objects.create(order=self.o, product_amount=3, product=self.p3)
        self.oi4 = OrderItem.objects.create(order=self.o, product_amount=4, product=self.p4)
        
    def test_topseller(self):
        """
        """
        ts = lfs.marketing.utils.get_topseller(2)

        self.assertEqual(len(ts), 2)

        self.assertEqual(ts[0], self.p4)    
        self.assertEqual(ts[1], self.p3)
