# django imports
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.core.utils

def send_order_received_mail(order):
    """Sends and order received mail to the shop customer.
    
    Customer information is taken from the provided order.
    """    
    shop = lfs.core.utils.get_default_shop()
    
    subject = _(u"Your order has been received")
    from_email = shop.from_email
    to = [order.customer_email]
    bcc = shop.get_notification_emails()
    
    # text
    text = render_to_string("mail/order_received_mail.txt", {"order" : order})    
    mail = EmailMultiAlternatives(
        subject=subject, body=text, from_email=from_email, to=to, bcc=bcc)
    
    html = render_to_string("mail/order_received_mail.html", {
        "order" : order
    })
    
    mail.attach_alternative(html, "text/html")    
    mail.send()