# -*- coding: utf-8 -*-

# python imports
import re

# django imports
from django.http import HttpResponse

# tagging imports
from tagging.models import Tag

# lfs imports
from lfs.catalog.models import Product
from lfs.tagging import utils as tagging_utils

STOP_WORDS = re.compile("(und|was|u\.|&|\d|mit|das|gehört|\ber|wohin|\?)", re.IGNORECASE)
SEPARATORS = re.compile("[\-_]")
def tag_products(request, source="description"):
    """Auto tags product on base of product description.
    """
    if source == "description":
        parser = tagging_utils.SimpleHTMLParser()
        for product in Product.objects.all():
            print product.name
            parser.feed(product.description)        
            Tag.objects.update_tags(product, "")

            data, amount = re.subn(r"[\W]*", "", parser.data)
            tags = re.split("\s*", data)
            for tag in tags:
                if tag:
                    Tag.objects.add_tag(product, tag)

    elif source == "name":
        for product in Product.objects.all():
            Tag.objects.update_tags(product, "")

            data, amount = STOP_WORDS.subn("", product.name)
            data, amount = SEPARATORS.subn(" ", data)

            tags = re.split("\s*", data)
            
            for tag in tags:
                if tag:
                    Tag.objects.add_tag(product, tag)
            
        return HttpResponse("")
