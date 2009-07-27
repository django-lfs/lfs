# python imports
import urllib
import datetime

# django imports
from django.http import HttpResponseRedirect
from django.utils import simplejson
from django.utils.functional import Promise
from django.utils.encoding import force_unicode

# lfs imports
import lfs.catalog.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop
from lfs.catalog.models import Category

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

    # We just keep the message two seconds.
    max_age = 2
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() +
        datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")

    response = HttpResponseRedirect(url)
    response.set_cookie("message", lfs_quote(msg), max_age=max_age, expires=expires)

    return response

def get_current_categories(request, object):
    """Returns all current categories based on given request
    """
    if object and object.content_type == "category":
        parents = object.get_parents()
        current_categories = [object]
        current_categories.extend(parents)
    elif object and object.content_type == "product":
        current_categories = []
        category = lfs.catalog.utils.get_current_product_category(request, object)
        while category:
            current_categories.append(category)
            category = category.parent
    else:
        current_categories = []

    return current_categories

def set_category_levels():
    """Creates category levels based on the position in hierarchy.
    """
    for category in Category.objects.all():
        category.level = len(category.get_parents()) + 1
        category.save()

class CategoryTree(object):
    """Represents a category tree.
    """
    def __init__(self, currents, start_level, expand_level):
        self.currents = currents
        self.start_level = start_level
        self.expand_level = expand_level

    def get_category_tree(self):
        """Returns a category tree
        """
        # NOTE: We don't use the level attribute of the category but calculate
        # actual position of a category based on the current tree. In this way
        # the category tree always start with level 1 (even if we start with 
        # category level 2) an the correct css is applied.
        level = 0
        categories = []
        for category in Category.objects.filter(level = self.start_level):

            if (self.currents and category in self.currents):
                children = self._get_sub_tree(category, level+1)
                is_current = True
            elif category.level <= self.expand_level:
                children = self._get_sub_tree(category, level+1)
                is_current = False
            else:
                children = []
                is_current = False

            if self.start_level > 1:
                if category.parent in self.currents:
                    categories.append({
                        "category" : category,
                        "children" : children,
                        "level" : level,
                        "is_current" : is_current,
                    })
            else:
                categories.append({
                    "category" : category,
                    "children" : children,
                    "level" : level,
                    "is_current" : is_current,
                })

        return categories

    def _get_sub_tree(self, category, level):
        categories = []
        for category in Category.objects.filter(parent = category):

            if (self.currents and category in self.currents):
                children = self._get_sub_tree(category, level+1)
                is_current = True
            elif category.level <= self.expand_level:
                children = self._get_sub_tree(category, level+1)
                is_current = False
            else:
                children = []
                is_current = False

            categories.append({
                "category" : category,
                "children" : children,
                "level" : level,
                "is_current" : is_current,
            })

        return categories