# django imports
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.settings import STANDARD_PRODUCT, VARIANT

def livesearch(request, template_name="search/livesearch_results.html"):
    """
    """
    phrase = request.GET.get("phrase", "")

    if phrase == "":
        result = simplejson.dumps({
            "state" : "failure",
        })
    else:
        # Products
        query = Q(name__icontains=phrase) & Q(sub_type__in = (STANDARD_PRODUCT, VARIANT))
        products = Product.objects.filter(query)[0:5]
        
        products = render_to_string(template_name, RequestContext(request, {
            "products" : products,
            "phrase" : phrase,
        }))
        
        result = simplejson.dumps({
            "state" : "success",
            "products" : products
        })
    return HttpResponse(result)
    
def search(request, template_name="search/search_results.html"):
    """
    """
    phrase = request.GET.get("phrase")
    
    # Products
    query = Q(name__icontains=phrase) & Q(sub_type__in = (STANDARD_PRODUCT, VARIANT))
    products = Product.objects.filter(query)

    total = 0
    if products:
        total += len(products)
        
    return render_to_response(template_name, RequestContext(request, {
        "products" : products,
        "phrase" : phrase,
    }))