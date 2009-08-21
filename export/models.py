# django imports
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.catalog.models import Product

class Export(models.Model):
    """An export of products.
    """
    name = models.CharField(_(u"Name"), max_length=100)
    products = models.ManyToManyField(Product, verbose_name=_(u"Products"), blank=True, related_name="exports")
    script = models.ForeignKey("Script", verbose_name=_(u"Script"))
    position = models.IntegerField(default=1)

    class Meta:
        ordering = ("position", "name")
        
    def __unicode__(self):
        return "%s.%s" % (self.module, self.method)

    def get_absolute_url(self):
        """
        """
        return reverse(
            "lfs_export", kwargs={ "export_id" : self.id })

    def get_products(self):
        """Returns selected products.
        """
        return self.products.all()
        
class Script(models.Model):
    """Represents an export script for an Export
    """
    module = models.CharField(max_length=255, default="lfs.export.generic")
    method = models.CharField(max_length=255, default="export")
    name = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return self.name 

    class Meta:
        ordering = ("name", )
        unique_together = ("module", "method")