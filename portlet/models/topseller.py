# django imports
from django import forms
from django.db import models
from django.template.loader import render_to_string

# portlets imports
from portlets.models import Portlet
from portlets.utils import register_portlet

# lfs imports
import lfs.marketing.utils

class TopsellerPortlet(Portlet):
    """A portlet to display recent visited products.
    """
    limit = models.IntegerField(default=5)

    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        category = context.get("category")
        if category is None:
            topseller = []
        else:
            topseller = lfs.marketing.utils.get_topseller_for_category(
                category, self.limit)
        
        return render_to_string("portlets/topseller.html", {
            "title" : self.title,
            "topseller" : topseller,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        })

    def form(self, **kwargs):
        """
        """
        return TopsellerForm(instance=self, **kwargs)

class TopsellerForm(forms.ModelForm):
    """
    """
    class Meta:
        model = TopsellerPortlet

register_portlet(TopsellerPortlet, "Topseller")