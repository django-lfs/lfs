# lfs imports
from lfs.core.signals import customer_added
from lfs.core.signals import order_submitted
from lfs.mail import utils as mail_utils

def order_submitted_listener(sender, **kwargs):
    """Listen to order submitted signal
    """
    mail_utils.send_order_received_mail(sender)
order_submitted.connect(order_submitted_listener)

def customer_added_listener(sender, **kwargs):
    """Listens to customer added signal.
    """
    mail_utils.send_customer_added(sender)
customer_added.connect(customer_added_listener)