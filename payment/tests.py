# django imports
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

# lfs imports
from lfs.core.models import Country
from lfs.order.models import Order
from lfs.payment.models import PayPalOrderTransaction

# other imports
from paypal.standard.ipn.models import PayPalIPN
import uuid




class PayPalPaymentTestCase(TestCase):
    """Tests paypal payments
    """
    fixtures = ['lfs_shop.xml']
    
    def setUp(self):
        
        self.uuid = "981242b5-fb0c-4563-bccb-e03033673d2a"
        self.IPN_POST_PARAMS = {
            "protection_eligibility":"Ineligible",
            "last_name":"User",
            "txn_id":"51403485VH153354B",
            "receiver_email":settings.PAYPAL_RECEIVER_EMAIL,
            "payment_status":"Completed",
            "payment_gross":"10.00",
            "tax":"0.00",
            "residence_country":"US",
            "invoice":"0004",
            "payer_status":"verified",
            "txn_type":"express_checkout",
            "handling_amount":"0.00",
            "payment_date":"23:04:06 Feb 02, 2009 PST",
            "first_name":"Test",
            "item_name":"Something from the shop",
            "charset":"windows-1252",
            "custom":self.uuid,
            "notify_version":"2.6",
            "transaction_subject":"",
            "test_ipn":"1",
            "item_number":"1",
            "receiver_id":"258DLEHY2BDK6",
            "payer_id":"BN5JZ2V7MLEV4",
            "verify_sign":"An5ns1Kso7MWUdW4ErQKJJJ4qi4-AqdZy6dD.sGO3sDhTf1wAbuO2IZ7",
            "payment_fee":"0.59",
            "mc_fee":"0.59",
            "mc_currency":"USD",
            "shipping":"0.00",
            "payer_email":"bishan_1233269544_per@gmail.com",
            "payment_type":"instant",
            "mc_gross":"10.00",
            "quantity":"1",}
        

        def fake_postback(self, test=True):
            """Perform a Fake PayPal IPN Postback request."""
            return 'VERIFIED'

        PayPalIPN._postback = fake_postback
        
        # Every test needs a client.
        self.client = Client()        
    
    def test_order_transaction_created(self):
        """Tests the shop values right after creation of an instance
        """
        country = Country(code="ie", name="Ireland")
        country.save()
        order = Order(invoice_country=country, shipping_country=country, uuid=self.uuid)
        order.save()
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalOrderTransaction.objects.all()), 0)
        post_params = self.IPN_POST_PARAMS        
        response = self.client.post(reverse('paypal-ipn'), post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        self.assertEqual(len(PayPalOrderTransaction.objects.all()), 1)        
        ipn_obj = PayPalIPN.objects.all()[0]
        
        self.assertEqual(ipn_obj.flag, False)
