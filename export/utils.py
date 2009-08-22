# lfs imports
import lfs.catalog.utils
from lfs.export.models import CategoryOption
from lfs.export.models import Export
from lfs.export.models import Script
from lfs.export.settings import CATEGORY_VARIANTS_DEFAULT
from lfs.export.settings import CATEGORY_VARIANTS_CHEAPEST
from lfs.export.settings import CATEGORY_VARIANTS_ALL

def register(method, name):
    """Registers a new export logic.
    """
    try:
        Script.objects.get(
            module=method.__module__, method=method.__name__)
    except Script.DoesNotExist:
        try:
            Script.objects.create(
                module=method.__module__, method=method.__name__, name=name)
        except:
            # Fail silently
            pass

def get_variants_option(product):
    """Returns the variants option for given category or None.
    """
    try:
        category = product.get_categories()[0]
    except IndexError:
        return None

    while category:
        try:
            category_option = CategoryOption.objects.get(category=category)
        except:
            category = category.parent
        else:
            return category_option.variants_option
    return None

def get_variants(product, export):
    """
    """
    variants_option = get_variants_option(product)
    if variants_option is None:
        variants_option = export.variants_option
    
    if variants_option == CATEGORY_VARIANTS_DEFAULT:
        return [product.get_default_variant()]
    elif variants_option == CATEGORY_VARIANTS_ALL:
        return product.get_variants()
    elif variants_option == CATEGORY_VARIANTS_CHEAPEST:
        return [product.get_default_variant()]