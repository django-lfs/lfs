# lfs imports
from lfs.core.signals import order_submitted
from lfs.mail import utils as mail_utils

def order_submitted_listener(sender, **kwargs):
    """Sends an order received mail after an order has been submitted.
    """
    mail_utils.send_order_received_mail(sender)
order_submitted.connect(order_submitted_listener)
