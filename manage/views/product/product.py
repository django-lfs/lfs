# django imports
from django.contrib.admin import widgets
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.settings import VARIANT
from lfs.core.utils import LazyEncoder
from lfs.manage.views.product.accessories import manage_accessories
from lfs.manage.views.product.categories import manage_categories
from lfs.manage.views.product.images import manage_images
from lfs.manage.views.product.properties import manage_properties
from lfs.manage.views.product.related_products import manage_related_products
from lfs.manage.views.product.seo import manage_seo

class ProductDataForm(ModelForm):
    """Form to add and edit master data of a product.
    """
    class Meta:
        model = Product
        fields = ("name", "slug", "sub_type", "sku", "price", "tax", 
            "short_description", "description", "for_sale", "for_sale_price")

class VariantDataForm(ModelForm):
    """Form to add and edit master data of a variant.
    """
    class Meta:
        model = Product
        fields = ("active_name", "name", "slug", "active_sku", "sku",
            "active_price", "price", "active_short_description", "short_description", "active_description", 
            "description", "for_sale", "for_sale_price", 
            "active_related_products")

class ProductDimensionForm(ModelForm):
    """Form to add and edit dimension data of a product.
    """
    class Meta:
        model = Product
        fields = ("weight", "width", "height", "length", "manage_stock_amount", 
                  "stock_amount", "manual_delivery_time", "delivery_time", 
                  "deliverable", "order_time", "ordered_at")
    
    def __init__(self, *args, **kwargs):
        super(ProductDimensionForm, self).__init__(*args, **kwargs)
        self.fields["ordered_at"].widget = widgets.AdminDateWidget()

@permission_required("manage_shop", login_url="/login/")
def product_dispatcher(request):
    """Dispatches to the first product. This is called when the shop user clicks
    on the manage products link.
    """
    try:
        product = Product.objects.all()[0]
        url = reverse("lfs_manage_product", kwargs={"product_id" : product.id})
    except IndexError:
        url = reverse("lfs_manage_add_product")
    
    return HttpResponseRedirect(url)

@permission_required("manage_shop", login_url="/login/")    
def manage_product(request, product_id, template_name="manage/product/product.html"):
    """Displays the whole manage/edit form for the product with the passed id.
    """
    product = Product.objects.get(pk=product_id)

    return render_to_response(template_name, RequestContext(request, {
        "product" : product,
        "product_data" : product_data_form(request, product_id),
        "categories" : manage_categories(request, product_id),
        "images" : manage_images(request, product_id),
        "properties" : manage_properties(request, product.id),
        "accessories" : manage_accessories(request, product.id),
        "related_products" : manage_related_products(request, product.id),
        "selectable_products" : selectable_products_inline(request, as_string=True),
        "seo" : manage_seo(request, product_id),
        "dimension" : dimension(request, product_id),
    }))

@permission_required("manage_shop", login_url="/login/")
def dimension(request, product_id, template_name="manage/product/dimension.html"):
    """Displays and updates the product dimension.
    """
    product = lfs_get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        form = ProductDimensionForm(instance=product, data=request.POST)
        if form.is_valid():
            form.save()
            form = ProductDimensionForm(instance=product)
            message = _(u"Product dimension has been saved.")
        else:
            message = _(u"Please correct the indicated errors.")
    else:
        form = ProductDimensionForm(instance=product)
        
    result = render_to_string(template_name, RequestContext(request, {
        "product" : product, 
        "form" : form
    }))
    
    if request.is_ajax():
        result = simplejson.dumps({
            "html" : result,
            "message" : message,
        }, cls = LazyEncoder)
        return HttpResponse(result)
    else:
        return result

@permission_required("manage_shop", login_url="/login/")    
def product_data_form(request, product_id, template_name="manage/product/data.html"):
    """Displays the product master data form within the manage product view.
    """
    product = Product.objects.get(pk=product_id)    
    
    if product.sub_type == VARIANT:
        form = VariantDataForm(instance=product)
    else:
        form = ProductDataForm(instance=product)
        
    return render_to_string(template_name, RequestContext(request, {
        "product" : product,
        "form" : form,
    }))
 
@permission_required("manage_shop", login_url="/login/")   
def selectable_products_inline(request, as_string=False,
    template_name="manage/product/selectable_products_inline.html"):
    """Displays the selectable products for the product view. (Used to switch
    quickly from one product to another.)
    """
    session = request.session
    
    if request.method == "POST":
        if request.POST.has_key("reset_page") and session.has_key("page"):
            del request.session["page"]
            
        page = request.session.get("page", 1)
            
        name_filter = request.POST.get(
            "name_filter", session.get("name_filter", ""))
        category_filter = request.POST.get(
            "category_filter", session.get("category_filter", ""))

        request.session["name_filter"] = name_filter
        request.session["category_filter"] = category_filter
    else:
        if request.GET.get("reset-filter"):
            if session.has_key("page"):
                del request.session["page"]
            if session.has_key("name_filter"):                
                del request.session["name_filter"]
            if session.has_key("category_filter"):
                del request.session["category_filter"]
            
        page = request.GET.get("page", session.get("page", 1))
        request.session["page"] = page
        name_filter = request.session.get("name_filter", "")
        category_filter = request.session.get("category_filter", "")
    
    filters = Q()
    if name_filter:
        filters &= Q(name__icontains=name_filter)

    if category_filter:
        if category_filter == "None":
            filters &= Q(categories=None)
        else:
            # First we collect all sub categories and using the `in` operator
            category = lfs_get_object_or_404(Category, pk=category_filter)
            categories = [category]
            categories.extend(category.get_all_children())
        
            filters &= Q(categories__in = categories)
    
    # Get products related to filter
    products = Product.objects.filter(filters).exclude(sub_type=VARIANT)
    
    # Arrange variants after the parent product
    # products = []
    # for product in products_temp:
    #     products.append(product)        
    #     for variant in product.variants.all():
    #         products.append(variant)

    paginator = Paginator(products, 30)
    page = paginator.page(page)
    
    if request.is_ajax():
        try:
            current_product = int(request.META.get("HTTP_REFERER").split("/")[-1])
        except (ValueError, IndexError, AttributeError):
            current_product = ""        
    else:
        try:
            current_product = int(request.path.split("/")[-1])
        except (ValueError, IndexError, AttributeError):
            current_product = ""
            
    result = render_to_string(template_name, RequestContext(request, {
        "paginator" : paginator, 
        "page" : page,
        "current_product" : current_product,
    }))
    
    if as_string:
        return result
    else:
        return HttpResponse(result)

# Actions
@permission_required("manage_shop", login_url="/login/")
def product_by_id(request, product_id):
    """Little helper which returns a product by id. (For the shop customer the 
    products are displayed by slug, for the manager by id).
    """
    product = Product.objects.get(pk=product_id)
    url = reverse("lfs.catalog.views.product_view", kwargs={"slug" : product.slug})
    return HttpResponseRedirect(url)
    
def add_product(request, template_name="manage/product/add_product.html"):
    """Shows a simplified product form and adds a new product.
    """
    if request.method == "POST":
        form = ProductDataForm(request.POST)
        if form.is_valid():
            new_product = form.save()
            url = reverse("lfs_manage_product", kwargs={"product_id" : new_product.id})
            return HttpResponseRedirect(url)
    else:
        form = ProductDataForm()
        
    return render_to_response(template_name, RequestContext(request, {
        "form" : form
    }))

@permission_required("manage_shop", login_url="/login/")
def delete_product(request, product_id):
    """Deletes product with passed id.
    """    
    product = lfs_get_object_or_404(Product, pk=product_id)
    product.delete()

    url = reverse("lfs_manage_product_dispatcher")
    return HttpResponseRedirect(url)

@permission_required("manage_shop", login_url="/login/")
def edit_product_data(request, product_id, template_name="manage/product/data.html"):
    """Edits the product with given.
    """
    product = lfs_get_object_or_404(Product, pk=product_id)
    
    if product.sub_type == VARIANT:
        form = VariantDataForm(instance=product, data=request.POST)
    else:
        form = ProductDataForm(instance=product, data=request.POST)
    
    if form.is_valid():
        form.save()
        if product.sub_type == VARIANT:
            form = VariantDataForm(instance=product)
        else:
            form = ProductDataForm(instance=product)
        
        message = "Productdata has been saved."
    else:
        message = "Please correct the indicated errors."
    
    form_html = render_to_string(template_name, RequestContext(request, {
        "product" : product,
        "form" : form,
    }))
        
    result = simplejson.dumps({
        "selectable_products" : selectable_products_inline(request, as_string=True),
        "form" : form_html,
        "message" : message,
    })
    
    return HttpResponse(result)