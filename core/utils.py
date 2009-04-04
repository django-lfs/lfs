# python imports
import urllib

# django imports
from django.http import HttpResponseRedirect
from django.utils import simplejson
from django.utils.functional import Promise
from django.utils.encoding import force_unicode 
from django.utils.translation import ugettext_lazy as _

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

def lfs_quote(string, encoding="utf-8"):
    """Encodes string to encoding before quoting.
    """
    return urllib.quote(string.encode(encoding))
    
def set_message_cookie(url, msg):
    """Creates response object with given url and adds message cookie with passed
    message.
    """
    response = HttpResponseRedirect(url)
    response.set_cookie("message", lfs_quote(msg))
    
    return response