# django imports
from django.core.exceptions import ObjectDoesNotExist

# lfs imports
from lfs.catalog.models import Product
from django.db import connection

def get_topseller(limit):
    """Returns the top seller.
    """    
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
        except ObjectDoesNotExist:            
            pass
            
    return products