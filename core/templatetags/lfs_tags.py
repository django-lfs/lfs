# django imports
from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.cart import utils as cart_utils
import lfs.catalog.utils
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.settings import PRODUCT_TYPE_LOOKUP
from lfs.core.models import Shop
from lfs.order.models import Order
from lfs.shipping import utils as shipping_utils
import lfs.utils.misc

register = template.Library()

@register.inclusion_tag('shop/google_analytics_tracking.html', takes_context=True)
def google_analytics_tracking(context):
    """Returns google analytics tracking code which has been entered to the 
    shop.
    """
    shop = lfs_get_object_or_404(Shop, pk=1)
    return {
        "ga_site_tracking" : shop.ga_site_tracking,
        "google_analytics_id" : shop.google_analytics_id,
    }

@register.inclusion_tag('shop/google_analytics_ecommerce.html', takes_context=True)
def google_analytics_ecommerce(context):
    """Returns google analytics e-commerce tracking code. This should be 
    displayed on the thank-you page.
    """
    request = context.get("request")
    order = request.session.get("order")
    shop = lfs_get_object_or_404(Shop, pk=1)
    
    # The order is removed from the session. It has been added after the order
    # has been payed within the checkou process. See order.utils for more.
    if request.session.has_key("order"):
        del request.session["order"]
    
    return {
        "order" : order,
        "ga_ecommerce_tracking" : shop.ga_ecommerce_tracking,
        "google_analytics_id" : shop.google_analytics_id,
    }

def _get_shipping(context):
    request = context.get("request")
    slug = request.path.split("/")[-1]
    
    product = lfs_get_object_or_404(Product, slug=slug)
    if product.deliverable == False:
        return {
            "deliverable" : False,
            "delivery_time" : shipping_utils.get_product_delivery_time(request, slug)
        }
    else:        
        return {
            "deliverable" : True,        
            "delivery_time" : shipping_utils.get_product_delivery_time(request, slug)
        }

@register.inclusion_tag('catalog/recent_products_portlet.html', takes_context=True)
def recent_products_portlet(context, instance=None):
    """Displays recent visited products.
    """
    slug_not_to_display = ""
    limit = settings.LFS_RECENT_PRODUCTS_LIMIT
    if instance:
        ctype = ContentType.objects.get_for_model(instance)
        if ctype.name == u"product":
            slug_not_to_display = instance.slug
            limit = LFS_RECENT_PRODUCTS_LIMIT + 1
        
    request = context.get("request")
    
    products = []
    for slug in request.session.get("RECENT_PRODUCTS", [])[:limit]:
        if slug == slug_not_to_display:
            continue
        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            pass
        else:
            products.append(product)

    return { "products": products }
    
@register.inclusion_tag('shipping/shipping_tag.html', takes_context=True)
def shipping(context):
    return _get_shipping(context)
    
@register.inclusion_tag('shipping/shipping_portlet.html', takes_context=True)
def shipping_portlet(context):
    """
    """
    return _get_shipping(context)
    
@register.inclusion_tag('catalog/sorting.html', takes_context=True)
def sorting(context):
    """
    """
    request = context.get("request")
    return {"current" : request.session.get("sorting")}

@register.inclusion_tag('catalog/breadcrumbs.html', takes_context=True)
def category_breadcrumbs(context, category):
    """
    """
    cache_key = "category-breadcrumbs-%s" % category.slug
    objects = cache.get(cache_key)
    if objects is not None:
        return objects
    
    objects = []
    while category is not None:
        objects.insert(0, category)
        category = category.parent
    
    result = {
        "objects" : objects,
        "MEDIA_URL" : context.get("MEDIA_URL"),
    }
    
    cache.set(cache_key, result)
    return result
        
@register.inclusion_tag('catalog/breadcrumbs.html', takes_context=True)
def product_breadcrumbs(context, product):
    """Displays breadcrumbs for given product. 
    
    Takes care of the last visited category if the product has more than one
    category.
    """
    try:
        if product.is_variant():
            parent_product = product.parent
        else:
            parent_product = product
    except ObjectDoesNotExist:
        return []
    else:
        request = context.get("request")
        category = lfs.catalog.utils.get_current_product_category(request, product)
        if category is None:
            return []
        else:
            objects = [product]
            while category is not None:
                objects.insert(0, category)
                category = category.parent
    
    result = {
        "objects" : objects,
        "MEDIA_URL" : context.get("MEDIA_URL"),
    }
    
    return result

@register.inclusion_tag('catalog/product_navigation.html', takes_context=True)
def product_navigation(context, product):
    """Provides previous and next product links.
    """
    request = context.get("request")
    sorting = request.session.get("sorting")

    slug = product.slug
    
    cache_key = "product-navigation-%s" % slug
    temp = None # cache.get(cache_key)
    if temp is not None:
        try:
            return temp[sorting]
        except KeyError:
            pass
    else:
        temp = dict()
        
    # To calculate the position we take only STANDARD_PRODUCT into account.
    # That means if the current product is a VARIANT we switch to its parent
    # product.
    if product.is_variant():
        product = product.parent
        slug = product.slug
        
    category = lfs.catalog.utils.get_current_product_category(request, product)
    if category is None:
        return {"display" : False }
    else:
        # First we collect all sub categories. This and using the in operator makes
        # batching more easier
        categories = [category]
        
        if category.show_all_products:
            categories.extend(category.get_all_children())

        if sorting is not None:
            products = Product.objects.filter(categories__in = categories).order_by(sorting)
        else:
            products = Product.objects.filter(categories__in = categories)
        
        product_slugs = [p.slug for p in products]
        product_index = product_slugs.index(slug)
        
        if product_index > 0:
            previous = product_slugs[product_index-1]
        else:
            previous = None
        
        total = len(product_slugs)
        if product_index < total-1:
            next = product_slugs[product_index+1] 
        else:
            next = None
    
        result = {
            "display" : True,
            "previous" : previous, 
            "next" : next,
            "current" : product_index+1,
            "total" : total,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        }
        
        temp[sorting] = result
        cache.set(cache_key, temp)
        
        return result

@register.inclusion_tag('catalog/sorting_portlet.html', takes_context=True)
def sorting_portlet(context):
    request = context.get("request")
    return {
        "current" : request.session.get("sorting"),
        "MEDIA_URL" : context.get("MEDIA_URL"),        
    }

@register.inclusion_tag('cart/cart_portlet.html', takes_context=True)
def cart_portlet(context):
    """
    """
    request = context.get("request")
    cart = cart_utils.get_cart(request)
    if cart is None:
        amount_of_items = None
        price = None
    else:
        amount_of_items = cart.amount_of_items
        price = cart_utils.get_cart_price(request, cart, total=True)
        
    return {
        "amount_of_items" : amount_of_items,
        "price" : price,
        "MEDIA_URL" : context.get("MEDIA_URL"),
    }

@register.inclusion_tag('shop/menu.html', takes_context=True)
def menu(context):
    """
    """
    request = context.get("request")
    current_categories = get_current_categories(request)
    
    categories = []
    for category in Category.objects.filter(parent = None):
        categories.append({
            "id" : category.id,
            "slug" : category.slug,
            "name" : category.name,
            "selected" : category in current_categories            
        })
    
    return {
        "categories" : categories,
        "MEDIA_URL" : context.get("MEDIA_URL"),
    }
    
@register.inclusion_tag('catalog/related_products_portlet.html', takes_context=True)
def related_products_portlet(context, product_id):
    """
    """
    product = lfs_get_object_or_404(Product, pk=product_id)
    return {
        "product" : product,
        "MEDIA_URL" : context.get("MEDIA_URL"),
    }
    
    
@register.inclusion_tag('catalog/categories_portlet.html', takes_context=True)
def categories_portlet(context, object=None):
    """Renders the categories portlet, which is actually the navigation of the 
    shop.
    
    Parameters:
    ===========

    object  : The object for which the portlet should be rendered. This is
              necessary to calculate current selected categories.
              
              It makes only sense to be a product or a cateogry. For all 
              other objects the portlet is not affected.              
    """
    if object:
        cache_key = "categories-portlet-%s" % object.slug
    else:
        cache_key = "categories-portlet"
        
    categories = cache.get(cache_key)
    if categories is not None:
        return categories
    
    request = context.get("request")
    if object and object.content_type == "category":
        parents = object.get_parents()
        current_categories = [object]
        current_categories.extend(parents)
    elif object and object.content_type == "product":
        current_categories = object.get_categories(with_parents=True)        
    else:
        current_categories = []
        
    categories = []
    for category in Category.objects.filter(parent = None):
        
        if category in current_categories:
            children = _categories_portlet_children(request, current_categories, category)
            is_current = True            
        else:
            children = ""
            is_current = False            
            
        categories.append({
            "slug" : category.slug,
            "name" : category.name,
            "url"  : category.get_absolute_url(),            
            "is_current" : is_current,
            "children" : children
        })

    result = {
        "categories" : categories,
        "MEDIA_URL" : context.get("MEDIA_URL"),
    }
    cache.set(cache_key, result)

    return result

# NOTE: The reason why not to use another inclusion_tag is that the request is 
# not available within an inclusion_tag if one inclusion_tag is called by 
# another. (Don't know why yet.)
def _categories_portlet_children(request, current_categories, category, level=1):
    """Returns the children of the given category as HTML. This is only called
    by categories_portlet.
    """
    categories = []
    for category in category.category_set.all():
        
        if category in current_categories:
            children = _categories_portlet_children(request, current_categories, category, level+1)
            is_current = True
        else:
            children = ""
            is_current = False
        
        categories.append({
            "slug" : category.slug,
            "name" : category.name,
            "url"  : category.get_absolute_url(),
            "level" : level,
            "is_current" : is_current,
            "children" : children,
        })
    
    result = render_to_string("catalog/categories_portlet_children.html", RequestContext(request, {
        "categories" : categories
    }))
    
    return result

# TODO: Move this to shop utils or similar
def get_current_categories(request):
    """Returns the current category based on the current path.
    """
    slug = get_slug_from_request(request)
        
    if slug.find(settings.CATEGORY_PREFIX) != -1:
        try:
            slug = slug.replace(settings.CATEGORY_PREFIX, "")
            category = Category.objects.get(slug=slug)
        except ObjectDoesNotExist:
            return []
        else:
            parents = category.get_parents()
            categories = [category]
            categories.extend(parents)

            return categories
    else:
        try:
            product = Product.objects.get(slug=slug)
        except ObjectDoesNotExist:
            return []
        else:
            category = lfs.catalog.utils.get_current_product_category(request, product)
            if category is None:
                return []
            
            categories = [category]    
            categories.extend(category.get_parents())

            return categories

# TODO: Move this to shop utils or similar
def get_slug_from_request(request):
    """Returns the slug of the currently displayed category.
    """
    slug = request.path.split("/")[-1]
    try:
        int(slug)
    except ValueError:
        pass
    else:
        slug = request.path.split("/")[-2]
    
    return slug
    
@register.filter
def currency(price, arg=None):
    """
    """
    # TODO: optimize
    price = lfs.utils.misc.FormatWithCommas("%.2f", price)
    
    # replace . and , for german format
    a, b = price.split(".")
    a = a.replace(",", ".")
    price = "%s,%s EUR" % (a, b)
    
    return price

@register.filter
def quantity(quantity):
    """Removes the decimal places when they are zero.
    
    Means "1.0" is transformed to "1", whereas "1.1" is not transformed at all.
    """
    if str(quantity).find(".") == -1:
        return quantity
    else: 
        return int(quantity)
        
@register.filter
def sub_type_name(sub_type, arg=None):
    """
    """
    try:
        return PRODUCT_TYPE_LOOKUP[sub_type]
    except KeyError:
        return ""

@register.filter
def multiply(score, pixel):
    """
    """
    return score * pixel
    