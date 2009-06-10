# django imports
from django.utils.translation import gettext_lazy as _

SUBMITTED = 0
PAID = 1
SENT = 2
CLOSED = 3
CANCELED = 4
PAYMENT_FAILED = 5

ORDER_STATES = [
    (SUBMITTED, _(u"Submitted")),
    (PAID, _(u"Paid")),
    (SENT, _(u"Sent")),
    (CLOSED, _(u"Closed")),
    (CANCELED, _(u"Canceled")),
    (PAYMENT_FAILED, _(u"Payment Failed")),
]