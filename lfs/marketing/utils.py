# django imports
from django.core.cache import cache

# lfs imports
from lfs.catalog.models import Product
from lfs.marketing.models import Topseller
from lfs.order.models import OrderItem
from django.db import connection

def get_topseller(limit=5):
    """Returns products with the most sales. Limited by given limit.
    """
    cache_key = "topseller"
    topseller = cache.get(cache_key)
    if topseller is not None:
        return topseller
    
    # TODO: Check Django 1.1's aggregation
    cursor = connection.cursor()
    cursor.execute("""SELECT product_id, sum(product_amount) as sum
                      FROM order_orderitem 
                      GROUP BY product_id
                      ORDER BY sum DESC limit %s""" % limit)
    
    products = []
    for topseller in cursor.fetchall():
        try:
            products.append(Product.objects.get(pk=topseller[0]))
        except Product.DoesNotExist:            
            pass
    
    for explicit_ts in Topseller.objects.all():
        position = explicit_ts.position - 1
        if position < 0:
            position = 0
        products.insert(position, explicit_ts.product)
    
    products = products[:limit]
    cache.set(cache_key, products)
    return products
    
def get_topseller_for_category(category, limit=5):
    """Returns products with the most sales withing given category. Limited by
    given limit.
    """
    # TODO: Check Django 1.1's aggregation

    cache_key = "topseller-%s" % category.id
    topseller = cache.get(cache_key)
    if topseller is not None:
        return topseller
    
    # 1. Get all sub catgegories of passed category
    categories = [category]
    categories.extend(category.get_all_children())    
    category_ids = [c.id for c in categories]
    
    # 2. Get all order items with products within these categories
    order_items = OrderItem.objects.filter(product__categories__in=category_ids)
    
    # 3. Calculate totals per product
    products = {}
    for order_item in order_items:
        if not products.has_key(order_item.product.id):
            products[order_item.product.id] = 0
        products[order_item.product.id] += order_item.product_amount
    
    # 4. Sort product ids on values
    products = products.items()
    products.sort(lambda a, b: cmp(b[1], a[1]))
    
    objects = []
    for product_id, quantity in products[:limit]:
        try:
            objects.append(Product.objects.get(pk=product_id))
        except Product.DoesNotExist:
            pass
            
    for explicit_ts in Topseller.objects.filter(product__categories__in=category_ids):
        position = explicit_ts.position - 1
        if position < 0:
            position = 0
        objects.insert(position, explicit_ts.product)
    
    objects = objects[:limit]
    cache.set(cache_key, objects)
    return objects