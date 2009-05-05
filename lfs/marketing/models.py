# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.catalog.models import Product

class Topseller(models.Model):
    """Selected products are in any case among topsellers.
    """
    product  = models.ForeignKey(Product, verbose_name=_(u"Product"))
    position = models.PositiveSmallIntegerField(_(u"Position"), default=1)
    
    class Meta:
        ordering = ["position"]
        
    def __unicode__(self):
        return "%s (%s)" % (self.product.name, self.position)