"""Provides several utilities for catalog related stuff.
"""

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
    
    This is needed if the category has more than one category to to display 
    breadcrumbs, selected menu points, etc. appropriately.
    """
    try:
        product_categories = product.get_categories()
        if len(product_categories) == 0:
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