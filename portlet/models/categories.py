# django imports
from django import forms
from django.template import RequestContext
from django.template.loader import render_to_string

# portlets
from portlets.models import Portlet
from portlets.utils import register_portlet

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.utils import get_current_product_category

class CategoriesPortlet(Portlet):
    """A portlet to display categories.
    """
    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        # Calculate current categories
        request = context.get("request")
        object = context.get("category") or context.get("product")
        if object and object.content_type == "category":
            parents = object.get_parents()
            current_categories = [object]
            current_categories.extend(parents)
        elif object and object.content_type == "product":
            current_categories = []
            category = get_current_product_category(request, object)
            while category:
                current_categories.append(category)
                category = category.parent

            # current_categories = object.get_categories(with_parents=True)
        else:
            current_categories = []

        categories = []
        for category in Category.objects.filter(parent = None):

            if category in current_categories:
                children = self._categories_portlet_children(
                    request, current_categories, category)
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

        return render_to_string("portlets/categories.html", {
            "title" : self.title,
            "categories" : categories,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        })

    def _categories_portlet_children(self, request, current_categories, category, level=1):
        """Returns the children of the given category as HTML.
        """
        categories = []
        for category in category.category_set.all():

            if category in current_categories:
                children = self._categories_portlet_children(
                    request, current_categories, category, level+1)
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

        result = render_to_string("portlets/categories_children.html",
            RequestContext(request, {"categories" : categories }))

        return result

    def form(self, **kwargs):
        """
        """
        return CategoriesPortletForm(instance=self, **kwargs)

class CategoriesPortletForm(forms.ModelForm):
    """
    """
    class Meta:
        model = CategoriesPortlet

register_portlet(CategoriesPortlet, "Categories")