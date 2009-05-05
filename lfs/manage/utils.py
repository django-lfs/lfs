# django imports
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.template.loader import render_to_string

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.models import Product

def cartesian_product(*seqin):
    """Calculates the cartesian product of given lists.
    """
    # Found in ASPN Cookbook
    def rloop(seqin, comb):
        if seqin:
            for item in seqin[0]:
                newcomb = comb + [item]
                for item in rloop(seqin[1:], newcomb):
                    yield item
        else:
            yield comb
    
    return rloop(seqin, [])
    
if __name__ == "__main__":
    for x in cartesian_product([u'5|11', u'7|15', u'6|12']):
        print x

def update_category_positions(category):
    """Updates the position of the children of the passed category.
    """
    i = 1
    for child in Category.objects.filter(parent=category):
        child.position = i
        child.save()        
        i+= 2        
                
def categories(request, template_name="product/categories.html"):
    """Returns all categories as HTML
    """
    current_categories = get_current_categories(request)
    
    categories = []
    for category in Category.objects.filter(parent = None):
        
        if category in current_categories:
            children = categories_children(request, category)
        else:
            children = ""
            
        categories.append({
            "slug" : category.slug,
            "name" : category.name,
            "url"  : category.get_absolute_url(),            
            "children" : children
        })
    
    return render_to_string(template_name, RequestContext(request, {
        "categories" : categories,
    }))    

def categories_children(request, category,
    template_name="product/categories_children.html"):
    """Returns the children of the given category as HTML.
    """
    categories = []
    current_categories = get_current_categories(request)    
    for category in category.category_set.all():
        
        if category in current_categories:
            children = categories_children(request, category)
        else:
            children = ""
        
        categories.append({
            "slug" : category.slug,
            "name" : category.name,
            "url"  : category.get_absolute_url(),
            "children" : children,
        })
    
    result = render_to_string(template_name, RequestContext(request, {
        "categories" : categories
    }))
    
    return result
    
def get_current_categories(request):
    """Returns the current category based on the current path.
    """
    slug = request.path.split("/")[-1]
    if request.path.find("category") != -1:
        try:
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
            return product.get_categories(with_parents=True)                