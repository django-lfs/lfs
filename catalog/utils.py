"""Provides several utilities for catalog related stuff.
"""

# django imports
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import connection

# import lfs
import lfs.catalog.models

# TODO implement this methods.
# Category
def get_current_category_slug(request):
    """Returns the current category.
    """
    pass

def get_current_category_id(request):
    """Returns the current category.
    """
    pass
    
def get_current_category(request):
    """Returns the current category.
    """
    pass

# Product
def get_current_product_slug(request):
    """Returns the current product id
    """
    pass
    
def get_current_product_id(request):
    """Returns the current product id
    """
    pass
    
def get_current_product(request):
    """Returns the current product
    """    
    pass
    
def get_current_product_category(request, product):
    """Returns product category based on actual categories of the given product
    and the last visited category. 
    
    This is needed if the category has more than one category to display
    breadcrumbs, selected menu points, etc. appropriately.
    """
    try:
        product_categories = product.get_categories()
        if len(product_categories) == 1:
            category = product_categories[0]
        else:
            last_category = request.session.get("last_category")

            if last_category is None:
                return product_categories[0]
                
            category = None                
            if last_category in product_categories:
                category = last_category                
            else:
                children = last_category.get_all_children()
                for product_category in product_categories:
                    if product_category in children:
                        category = product_category
                        break
            if category is None:
                category = product_categories[0]
    except IndexError:            
        return None
    else:
        request.session["last_category"] = category
        return category

def get_property_groups(category):
    """Returns all property groups for given category
    """
    cache_key = "category-property-groups-%s" % category.id
    pgs = cache.get(cache_key)
    if pgs is not None:
        return pgs

    products = category.get_products()
    pgs = lfs.catalog.models.PropertyGroup.objects.filter(
        products__in=products).distinct()

    cache.set(cache_key, pgs)
    return pgs

def get_price_filters(category, product_filter, price_filter):
    """Creates price filter links based on the min and max price of the 
    categorie's products.
    """
    # Base are the filtered products
    products = get_filtered_products_for_category(category, product_filter, price_filter, None)
    if not products: 
        return []

    # And their variants
    all_products = []
    for product in products:
        all_products.append(product)
        all_products.extend(product.variants.all())
    
    product_ids = [p.id for p in all_products]
    
    # If a price filter is set we return just this.
    if price_filter:
        min = price_filter["min"]
        max = price_filter["max"]
        products = lfs.catalog.models.Product.objects.filter(
            effective_price__range=(min, max), pk__in=product_ids)
        quantity = len(products)
        
        return ({
            "min" : min, 
            "max" : max,
        },)
        
    product_ids_str = ", ".join([str(p.id) for p in all_products])
    cursor = connection.cursor()
    cursor.execute("""SELECT min(effective_price), max(effective_price)
                      FROM catalog_product
                      WHERE id IN (%s)""" % product_ids_str)
                      
    pmin, pmax = cursor.fetchall()[0]
    if pmax == pmin:
        step = pmax
    else:
        diff = pmax - pmin
        step = diff / 3
        
    if step >= 0 and step < 3:
        step = 3
    elif step >= 3 and step < 6:
        step = 5    
    elif step >= 6 and step < 11:
        step = 10
    elif step >= 11 and step < 51:
        step = 50
    elif step >= 51 and step < 101:
        step = 100
    elif step >= 101 and step < 501:
        step = 500
    elif step >= 501 and step < 1001:
        step = 1000        
    elif step >= 1000 and step < 5001:
        step = 500
    elif step >= 5001 and step < 10001:
        step = 1000
    
    result = []
    for n, i in enumerate(range(0, int(pmax), step)):
        if i > pmax:
            break
        min = i+1
        max = i+step
        products = lfs.catalog.models.Product.objects.filter(effective_price__range=(min, max), pk__in=product_ids)
        result.append({
            "min" : min,
            "max" : max,
            "quantity" : len(products),
        })
    
    # return result
    
    new_result = []
    for n, f in enumerate(result):
        if f["quantity"] == 0:
            try:
                result[n+1]["min"] = f["min"]
            except IndexError:
                pass
            continue
        new_result.append(f)
        
    return new_result

def get_product_filters(category, product_filter, price_filter, sorting):
    """Returns the next product filters based on products which are in the given 
    category and within the result set of the current filters.
    """
    properties_mapping = get_property_mapping()
    options_mapping = get_option_mapping()
    
    # Base are the filtered products
    products = get_filtered_products_for_category(category, product_filter, price_filter, sorting)
    if not products: 
        return []
    
    # And their variants
    all_products = []
    for product in products:
        all_products.append(product)
        all_products.extend(product.variants.all())

    product_ids = ", ".join([str(p.id) for p in all_products])

    # Count entries for current filter
    cursor = connection.cursor()
    cursor.execute("""SELECT property_id, value, parent_id
                      FROM catalog_productpropertyvalue
                      WHERE product_id IN (%s)""" % product_ids)

    already_count = {}
    amount = {}
    for row in cursor.fetchall():        
        # We count a property/value pair just one time per product
        if already_count.has_key("%s%s%s" % (row[2], row[0], row[1])):
            continue
        already_count["%s%s%s" % (row[2], row[0], row[1])] = 1
    
        if not amount.has_key(row[0]):
            amount[row[0]] = {}

        if not amount[row[0]].has_key(row[1]):
            amount[row[0]][row[1]] = 0
    
        amount[row[0]][row[1]] += 1    
    
    cursor.execute("""SELECT property_id, value
                      FROM catalog_productpropertyvalue
                      WHERE product_id IN (%s)
                      GROUP BY property_id, value""" % product_ids)

    # Group properties and values (for displaying)
    set_filters = dict(product_filter)
    properties = {}
    for row in cursor.fetchall():
        
        if properties_mapping[row[0]].filterable == False:
            continue
            
        if properties.has_key(row[0]) == False:
            properties[row[0]] = []

        # If the property is a select field we want to display the name of the 
        # option instead of the id.
        if properties_mapping[row[0]].is_select_field:
            try:
                name = options_mapping[row[1]].name
            except KeyError:
                name = row[1]
        else:
            name = row[1]
        
        # if the property within the set filters we just show the selected value
        if str(row[0]) in set_filters.keys():
            if str(row[1]) in set_filters.values():
                properties[row[0]] = ({
                    "id"       : row[0],
                    "value"    : row[1],
                    "name"     : name,
                    "quantity" : amount[row[0]][row[1]],
                    "show_quantity" : False,
                },)
            break
        else:
            properties[row[0]].append({
                "id"       : row[0],
                "value"    : row[1],
                "name"     : name,
                "quantity" : amount[row[0]][row[1]],
                "show_quantity" : True,
            })
    
    # Transform the group properties into a list of dicts
    result = []
    for property_id, values in properties.items():
        result.append({
            "id"    : property_id,
            "name"  : properties_mapping[property_id].name,
            "items" : values
        })
    
    return result

# TODO: Maybe we should pass here filters and sorting instead of the request.
def get_filtered_products_for_category(category, filters, price_filter, sorting):
    """Returns products for given categories and current filters sorted by 
    current sorting.
    """
    if filters:
        if category.show_all_products:
            products = category.get_all_products()
        else:
            products = category.get_products()
        
        # Generate ids for collected products
        product_ids = [str(p.id) for p in products]
        product_ids = ", ".join(product_ids)
    
        # Generate filter
        temp = []
        for f in filters:
            temp.append("property_id='%s' AND value='%s'" % (f[0], f[1]))
    
        fstr = " OR ".join(temp)
    
        # TODO: Will this work with every DB?
        
        # Get all product ids with matching filters. The idea behind this SQL 
        # query is: If for every filter (property=value) for a product id exists
        # a "product property value" the product matches. 
        cursor = connection.cursor()
        cursor.execute("""
            SELECT product_id, count(*) as amount
            FROM catalog_productpropertyvalue
            WHERE product_id IN (%s) and %s
            GROUP BY product_id
            HAVING amount=%s""" % (product_ids, fstr, len(filters)))
    
        matched_product_ids = [row[0] for row in cursor.fetchall()]
        
        # All variants of category products
        all_variants = lfs.catalog.models.Product.objects.filter(parent__in=products)
        
        if all_variants:
            all_variant_ids = [str(p.id) for p in all_variants]
            all_variant_ids = ", ".join(all_variant_ids)
        
            # Variants with matching filters
            cursor.execute("""
                SELECT product_id, count(*) as amount
                FROM catalog_productpropertyvalue
                WHERE product_id IN (%s) and %s
                GROUP BY product_id
                HAVING amount=%s""" % (all_variant_ids, fstr, len(filters)))
        
            # Get the parent ids of the variants as the "product with variants" 
            # should be displayed and not the variants.            
            variant_ids = [str(row[0]) for row in cursor.fetchall()]
            if variant_ids:
                variant_ids = ", ".join(variant_ids)
            
                cursor.execute("""
                    SELECT parent_id
                    FROM catalog_product
                    WHERE id IN (%s)""" % variant_ids)
        
                parent_ids = [str(row[0]) for row in cursor.fetchall()]        
                matched_product_ids.extend(parent_ids)
        
        # As we factored out the ids of all matching products now, we get the 
        # product instances in the correct order
        products = lfs.catalog.models.Product.objects.filter(pk__in=matched_product_ids)
    else:
        categories = [category]
        if category.show_all_products:
            categories.extend(category.get_all_children())
        products = lfs.catalog.models.Product.objects.filter(categories__in=categories)
    
    if price_filter:
        products = products.filter(effective_price__range=[price_filter["min"], price_filter["max"]])
    
    if sorting:
        products = products.order_by(sorting)
        
    return products

def get_option_mapping():
    """Returns a dictionary with property id to property name.
    """
    options = {}
    for option in lfs.catalog.models.PropertyOption.objects.all():
        options[str(option.id)] = option
    return options
    
def get_property_mapping():
    """Returns a dictionary with property id to property name.
    """
    properties = {}
    for property in lfs.catalog.models.Property.objects.all():
        properties[property.id] = property
    
    return properties