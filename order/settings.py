# django imports
from django.utils.translation import gettext_lazy as _

SUBMITTED = 0
PAYED = 1
SENT = 2
CLOSED = 3
CANCELED = 4

ORDER_STATES = [
    (SUBMITTED, _(u"Submitted")),
    (PAYED, _(u"Payed")),
    (SENT, _(u"Sent")),
    (CLOSED, _(u"Closed")),
    (CANCELED, _(u"Canceled")),
]