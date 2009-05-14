# lfs imports
from lfs.order.models import Order
from models import PayPalOrderTransaction

# other imports
import logging
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from paypal.standard.pdt.signals import pdt_failed, pdt_successful

def mark_payment(pp_obj, payment=True):
    order = None
    try:
        logging.info("getting order for uuid %s"%pp_obj.custom)
        order_uuid = pp_obj.custom
        order = Order.objects.get(uuid=order_uuid)
        if order is not None:
            order.paid = payment
        order.save()
    except Order.DoesNotExist, e:
        logging.error(e)
    return order

def successful_payment(sender, **kwargs):
    logging.info("successful ipn payment")    
    ipn_obj = sender    
    order = mark_payment(ipn_obj, True)
    if order is not None:
        transaction, created = PayPalOrderTransaction.objects.get_or_create(order=order)
        transaction.ipn.add(ipn_obj)
        transaction.save()
    else:
        logging.warning("successful ipn payment, no order found for uuid %s"%ipn_obj.custom)
        
def unsuccessful_payment(sender, **kwargs):
    logging.info("unsuccessful ipn payment")    
    ipn_obj = sender    
    order = mark_payment(ipn_obj, False)    
    if order is not None:
        transaction, created = PayPalOrderTransaction.objects.get_or_create(order=order)
        transaction.ipn.add(ipn_obj)
        transaction.save()
    else:
        logging.warning("unsuccessful ipn payment, no order found for uuid %s"%ipn_obj.custom)

def successful_pdt(sender, **kwargs):    
    logging.info("successful pdt payment")
    pdt_obj = sender    
    order = mark_payment(pdt_obj, True)
    
def unsuccesful_pdt(sender, **kwargs):
    logging.info("unsuccessful pdt payment")
    pdt_obj = sender
    order = mark_payment(pdt_obj, False)    
    
payment_was_successful.connect(successful_payment, dispatch_uid="Order.ipn_successful")
payment_was_flagged.connect(unsuccessful_payment, dispatch_uid="Order.ipn_unsuccessful")
pdt_successful.connect(successful_pdt, dispatch_uid="Order.pdt_successful")
pdt_failed.connect(unsuccesful_pdt, dispatch_uid="Order.pdt_unsuccessful")
    