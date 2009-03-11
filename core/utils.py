# django imports
from django.utils import simplejson
from django.utils.functional import Promise
from django.utils.encoding import force_unicode 

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop

class LazyEncoder(simplejson.JSONEncoder): 
    """Encodes django's lazy i18n strings.
    """
    def default(self, obj): 
        if isinstance(obj, Promise): 
            return force_unicode(obj) 
        return obj 
        
def get_default_shop():
    """Returns the default shop. At the moment this the shop with id == 1.
    """
    return lfs_get_object_or_404(Shop, pk=1)