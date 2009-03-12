# django imports
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.cart.views import add_to_cart
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS, VARIANT
from lfs.catalog.settings import SELECT
from lfs.catalog.settings import CONTENT_PRODUCTS
import lfs.catalog.utils
from lfs.core.signals import lfs_sorting_changed
from lfs.utils import misc as lfs_utils

def set_sorting(request):
    """Saves the given sortings (by request body) to session.
    """
    sorting = request.POST.get("sorting", "")
    if sorting == "" and request.session.has_key("sorting"):
        del request.session["sorting"]
    else:
        request.session["sorting"] = sorting
    
    # lfs_sorting_changed.send(category_id)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    
def category_view(request, slug, start=0, template_name="catalog/category.html"):
    """
    """
    category = lfs_get_object_or_404(Category, slug=slug)
    
    if category.content == CONTENT_PRODUCTS:
        inline = category_products(request, slug, start)
    else:
        inline = category_categories(request, slug)
    
    # Set last visited category for later use, e.g. Display breadcrumbs, 
    # selected menu points, etc.
    request.session["last_category"] = category
    
    return render_to_response(template_name, RequestContext(request, {
        "category" : category,
        "category_inline" : inline
    }))

def category_categories(request, slug, template_name="catalog/category_categories.html"):
    """Displays the child categories of the category with passed slug.

    This is displayed if the category's content attribute is set to categories".
    """
    cache_key = "category-categories-%s" % slug

    result = cache.get(cache_key)    
    if result is not None:
        return result
        
    category = lfs_get_object_or_404(Category, slug=slug)

    format_info = category.get_format_info()
    amount_of_cols = format_info["category_cols"]
    
    categories = []
    row = []
    for i, category in enumerate(category.get_children()):
        row.append(category)
        if (i+1) % amount_of_cols == 0:
            categories.append(row)
            row = []
    
    if len(row) > 0:
        categories.append(row)

    result = render_to_string(template_name, {
        "category" : category,
        "categories" : categories,        
    })
    
    cache.set(cache_key, result)
    return result
    
def category_products(request, slug, start=0, template_name="catalog/category_products.html"):
    """Displays the products of the category with passed slug.
    
    This is displayed if the category's content attribute is set to products.
    """
    sorting = request.session.get("sorting")
    
    cache_key = "category-products-%s" % slug
    temp = cache.get(cache_key)
    if temp is not None:
        try:
            return temp["%s-%s" % (start, sorting)]
        except KeyError:
            pass
    else:
        temp = dict()
    
    category = lfs_get_object_or_404(Category, slug=slug)
    
    # Calculates parameters for display.
    start = int(start)
    format_info = category.get_format_info()
    amount_of_rows = format_info["product_rows"]
    amount_of_cols = format_info["product_cols"]
    amount = amount_of_rows * amount_of_cols

    # First we collect all sub categories. This and using the in operator makes
    # batching more easier
    categories = [category]
    if category.show_all_products:
        categories.extend(category.get_all_children())
    
    if sorting is not None:
        all_products = Product.objects.filter(categories__in = categories).order_by(sorting)
    else:
        all_products = Product.objects.filter(categories__in = categories)
        
    # Calculate products
    row = []
    products = []
    for i, product in enumerate(all_products[start:start+amount]):
        row.append(product)
        if (i+1) % amount_of_cols == 0:
            products.append(row)
            row = []
    
    if len(row) > 0:
        products.append(row)

    amount_of_products = all_products.count()
            
    # Calculate urls
    pages = []
    for i in range(0, amount_of_products/amount):
        page_start = i*amount
        pages.append({
            "name" : i+1,
            "start" : page_start,
            "selected" : start == page_start,
        })
    
    if (start + amount) < amount_of_products:
        next_url = "%s/%s" % (category.get_absolute_url(), start + amount)
    else:
        next_url = None        
    
    if (start - amount) >= 0:
        previous_url = "%s/%s" % (category.get_absolute_url(), start - amount)
    else:
        previous_url = None
    
    result = render_to_string(template_name, RequestContext(request, {
        "category" : category,
        "products" : products,        
        "next_url" : next_url,
        "previous_url" : previous_url,
        "amount_of_products" : amount_of_products,
        "pages" : pages,
        "show_pages" : len(pages) > 1,
    }))
    
    temp["%s-%s" % (start, sorting)] = result
    cache.set(cache_key, temp)
    return result
    
def product_view(request, slug, template_name="catalog/product.html"):
    """Main view to display a product.
    """    
    product = lfs_get_object_or_404(Product, slug=slug)
    
    # Store recent products for later use
    recent = request.session.get("RECENT_PRODUCTS", [])
    if slug in recent:
        recent.remove(slug)
    recent.insert(0, slug)
    if len(recent) > settings.LFS_RECENT_PRODUCTS_LIMIT:
        recent = recent[:settings.LFS_RECENT_PRODUCTS_LIMIT+1]
    request.session["RECENT_PRODUCTS"] = recent
    
    # TODO: Factor current_category out to a inclusion tag, so that people can
    # let it away if they don't need it.
    return render_to_response(template_name, RequestContext(request, {
        "product_inline" : product_inline(request, product.id),
        "product" : product,
        "current_category" : lfs.catalog.utils.get_current_product_category(request, product),
    }))

def product_inline(request, id, template_name="catalog/product_inline.html"):
    """Part of the prduct view, which displays the actual data of the product.
    
    This is factored out to be able to better cached and in might in future used
    used to be updated via ajax requests.
    """
    cache_key = "product-inline-%s" % id
    result = cache.get(cache_key)
    if result is not None:
        return result
        
    # Get product in question
    product = lfs_get_object_or_404(Product, pk=id)
    
    if product.sub_type == PRODUCT_WITH_VARIANTS:
        variant = product.get_default_variant()
        if variant is None:
            variant = product
    elif product.sub_type == VARIANT:
        variant = product
        product = product.parent
    else:
        variant = product

    properties = []
    variants = []
    if product.variants_display_type == SELECT:
        # Get all properties (sorted). We need to traverse through all
        # property/options to select the options of the current variant.
        for property in product.properties.order_by("productproperties"):
            options = []
            for property_option in property.propertyoption_set.all():
                if variant.has_option(property, property_option):
                    selected = True
                else:
                    selected = False
                options.append({
                    "id"   : property_option.id,
                    "name" : property_option.name,
                    "selected" : selected
                })
            properties.append({
                "id" : property.id,
                "name" : property.name,
                "options" : options                
            })
    else:
        properties = product.properties.order_by("productproperties")
        variants = product.get_variants()
    
    # Reviews 
    
    result = render_to_string(template_name, RequestContext(request, {
        "product" : product,
        "variant" : variant,
        "variants" : variants,
        "product_accessories" : variant.get_accessories(),
        "properties" : properties
    }))
    
    cache.set(cache_key, result)
    return result
    
def product_form_dispatcher(request):
    """Dispatches to the added-to-cart view or to the selected variant. 
    
    This is needed as the product form can have several submit buttons:
       - The add-to-cart button
       - The switch to the selected variant button (only in the case the 
         variants of of the product are displayed as select box. This may change 
         in future, when the switch may made with an ajax request.)
    """
    if request.POST.get("add-to-cart") is not None:
        return add_to_cart(request)
    else:        
        product_id = request.POST.get("product_id")
        product = Product.objects.get(pk=product_id)

        options = lfs_utils.parse_properties(request)
        variant = product.get_variant(options)
        
        if variant is None:
            variant = product.get_default_variant()
        
        return HttpResponseRedirect(variant.get_absolute_url())

# NOT used at moment
def get_category_nodes(request):
    """Returns the category tree as JSON for extJS.
    """
    categories = []
    for category in Category.objects.filter(parent = None):
        temp = _get_children_nodes(category)
        categories.append({
            "id" : category.slug,
            "text" : category.name,
            "leaf" : len(temp) == 0,
            "children" : temp
        })
            
    return HttpResponse(simplejson.dumps(categories))
    
def _get_children_nodes(category):
    """
    """ 
    children = []
    for category in category.category_set.all():
        temp = _get_children_nodes(category)
        children.append({
            "id" : category.slug,
            "text" : category.name,
            "leaf" : len(temp) == 0,
            "children" : temp,
        })
        
    return children
