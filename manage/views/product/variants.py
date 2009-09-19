# django imports
from django.contrib.auth.decorators import permission_required
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm
from django.http import HttpResponse
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils import simplejson

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.signals import product_changed
from lfs.catalog.models import Product
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import ProductsPropertiesRelation
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyGroup
from lfs.catalog.models import PropertyOption
from lfs.catalog.settings import VARIANT, PROPERTY_SELECT_FIELD
import lfs.catalog.utils
from lfs.manage import utils as manage_utils


class PropertyOptionForm(ModelForm):
    """Form to add/edit property options.
    """
    class Meta:
        model = PropertyOption
        fields = ("name", )

class PropertyForm(ModelForm):
    """Form to add/edit properties.
    """
    class Meta:
        model = Property
        fields = ("name", )

class ProductVariantSimpleForm(ModelForm):
    """Form to add/edit variants options.
    """
    class Meta:
        model = Product
        fields = ("slug", "name", "price", )

class DisplayTypeForm(ModelForm):
    """Form to add/edit product's sub types.
    """
    class Meta:
        model = Product
        fields = ("variants_display_type", )

@permission_required("manage_shop", login_url="/login/")
def manage_variants(request, product_id, as_string=False, template_name="manage/product/variants.html"):
    """Manages the variants of a product.
    """
    product = Product.objects.get(pk=product_id)

    property_form = PropertyForm()
    property_option_form = PropertyOptionForm()
    variant_simple_form = ProductVariantSimpleForm()
    display_type_form = DisplayTypeForm(instance=product)

    # TODO: Delete cache when delete options
    cache_key = "manage-properties-variants-%s" % product_id
    variants = cache.get(cache_key)
    # Get all properties. We need to traverse through all property / options
    # in order to select the options of the current variant.
    if variants is None:
        variants = []
        for variant in product.variants.all().order_by("variant_position"):
            properties = []
            for property in product.get_properties():
                options = []
                for property_option in property.options.all():
                    if variant.has_option(property, property_option):
                        selected = True
                    else:
                        selected = False
                    options.append({
                        "id"   : property_option.id,
                        "name" : property_option.name,
                        "selected" : selected
                    })
                properties.append({
                    "id" : property.id,
                    "name" : property.name,
                    "options" : options
                })

            variants.append({
                "id" : variant.id,
                "active" : variant.active,
                "slug" : variant.slug,
                "sku" : variant.sku,
                "name" : variant.name,
                "price" : variant.price,
                "position" : variant.variant_position,
                "properties" : properties
            })

        cache.set(cache_key, variants)

    # Generate list of all property groups; used for group selection
    product_property_group_ids = [p.id for p in product.property_groups.all()]
    shop_property_groups = []
    for property_group in PropertyGroup.objects.all():

        shop_property_groups.append({
            "id" : property_group.id,
            "name" : property_group.name,
            "selected" : property_group.id in product_property_group_ids,
        })

    result = render_to_string(template_name, RequestContext(request, {
        "product" : product,
        "variants" : variants,
        "shop_property_groups" : shop_property_groups,
        "local_properties" : product.get_local_properties(),
        "all_properties" : product.get_properties(),
        "property_option_form" : property_option_form,
        "property_form" : property_form,
        "variant_simple_form" : variant_simple_form,
        "display_type_form" : display_type_form,
    }))

    if as_string:
        return result
    else:
        return HttpResponse(result)

# Actions
@permission_required("manage_shop", login_url="/login/")
def add_property(request, product_id):
    """Adds a new property to the product with given product id.
    """
    product = Product.objects.get(pk=product_id)
    property_form = PropertyForm(data=request.POST)
    if property_form.is_valid():
        property = property_form.save(commit=False)
        property.type = PROPERTY_SELECT_FIELD
        property.local = True

        # it doesn't make sense to filter by local properties as every local
        # property has an own id. Maybe we can do this with an grouping id or
        # something like that
        property.filterable = False

        property.save()
        product_property = ProductsPropertiesRelation(product=product, property=property, position=999)
        product_property.save()

        # Refresh positions
        for i, product_property in enumerate(product.productsproperties.all()):
            product_property.position = i
            product_property.save()

    return HttpResponse(manage_variants(request, product_id))

@permission_required("manage_shop", login_url="/login/")
def delete_property(request, product_id, property_id):
    """Deletes property with passed property id.
    """
    try:
        property = Property.objects.get(pk=property_id)
        product = Product.objects.get(pk=product_id)
    except ObjectDoesNotExist:
        pass
    else:
        property.delete()

    return HttpResponse(manage_variants(request, product_id))

@permission_required("manage_shop", login_url="/login/")
def change_property_position(request):
    """Changes property position based on parameters passed by request body.
    """
    product_id = request.GET.get("product_id")
    property_id = int(request.GET.get("property_id"))
    direction = request.GET.get("direction")

    try:
        product_property = ProductsPropertiesRelation.objects.get(product = product_id, property = property_id)
    except ObjectDoesNotExist:
        pass
    else:
        if direction == "up":
            product_property.position -= 3
        else:
            product_property.position += 3

        product_property.save()

    _refresh_property_positions(product_id)

    return HttpResponse(manage_variants(request, product_id))

@permission_required("manage_shop", login_url="/login/")
def add_property_option(request, product_id):
    """Adds a new option to the property with given property id.

    NOTE: The reason why to pass the product id here is to be able to redirect
    to the product. Properties can belong to more than one product.

    TODO: Do this with REFERER
    """
    property_option_form = PropertyOptionForm(data=request.POST)
    if property_option_form.is_valid():
        names = request.POST.get("name").split(",")
        position = 999
        for name in names:
            property_option = PropertyOption(name=name)
            property_option.property_id = request.POST.get("property_id")
            property_option.position = position
            property_option.save()
            position += 1

        # Refresh positions
        for i, option in enumerate(PropertyOption.objects.filter(property = property_option.property)):
            option.position = i
            option.save()

    return HttpResponse(manage_variants(request, product_id))

@permission_required("manage_shop", login_url="/login/")
def delete_property_option(request, product_id, option_id):
    """Deletes property option with passed option id.
    """
    try:
        property_option = PropertyOption.objects.get(pk=option_id)
        product = Product.objects.get(pk=product_id)
    except ObjectDoesNotExist:
        pass
    else:
        property_option.delete()

    return HttpResponse(manage_variants(request, product_id))

@permission_required("manage_shop", login_url="/login/")
def add_variants(request, product_id):
    """Adds variants to product with passed product_id based on property/option-
    combinations passed within request body.
    """
    cache.delete("variants%s" % product_id)

    product = Product.objects.get(pk=product_id)

    # Add variant(s)
    variant_simple_form = ProductVariantSimpleForm(data=request.POST)

    # We don't have to check whether the form is valid. If the fields
    # are empty we create default ones.

    # First we need to prepare the requested properties for the use
    # with cartesian product. That means if the keyword "all" is
    # found we collect all options of this properties.
    properties = []
    for key, value in request.POST.items():
        if key.startswith("property"):
            property_id = key.split("_")[1]
            if value == "all":
                temp = []
                for option in PropertyOption.objects.filter(property=property_id):
                    temp.append("%s|%s" % (property_id, option.id))
                properties.append(temp)
            else:
                properties.append(["%s|%s" % (property_id, value)])

    # Create a variant for every requested option combination
    for i, options in enumerate(manage_utils.cartesian_product(*properties)):

        if product.has_variant(options):
            continue

        price = request.POST.get("price")

        slug = ""
        for option in options:
            property_id, option_id = option.split("|")
            o = PropertyOption.objects.get(pk=option_id)
            slug += "-" + slugify(o.name)

        slug = "%s%s" % (product.slug, slug)
        sku = "%s-%s" % (product.sku, i+1)

        variant = Product(slug=slug, sku=sku, parent=product, price=price, variant_position=i+1, sub_type=VARIANT)
        variant.save()

        # Save the value for this product and property
        for option in options:
            property_id, option_id = option.split("|")
            pvo = ProductPropertyValue(product = variant, property_id = property_id, value=option_id)
            pvo.save()

    from lfs.manage.views.product.product import selectable_products_inline
    result = simplejson.dumps({
        "properties" : manage_variants(request, product_id, as_string=True),
    })

    return HttpResponse(result)

@permission_required("manage_shop", login_url="/login/")
def update_variants(request, product_id):
    """Updates/Deletes variants with passed ids (via request body) dependent on
    given action (also via request body).
    """
    product = lfs_get_object_or_404(Product, pk=product_id)

    action = request.POST.get("action")
    if action == "delete":
        for key in request.POST.keys():
            if key.startswith("delete-"):
                try:
                    id = key.split("-")[1]
                    variant = Product.objects.get(pk=id)
                except (IndexError, ObjectDoesNotExist):
                    continue
                else:
                    variant.delete()
    elif action == "update":
        for key, value in request.POST.items():
            if key.startswith("variant-"):
                id = key.split("-")[1]
                try:
                    variant = Product.objects.get(pk=id)
                except ObjectDoesNotExist:
                    continue
                else:
                    for name in ("slug", "sku", "price"):
                        value = request.POST.get("%s-%s" % (name, id))
                        if value != "":
                            setattr(variant, name, value)

                    # name
                    variant.name = request.POST.get("name-%s" % id)

                    # active
                    active = request.POST.get("active-%s" % id)
                    if active:
                        variant.active = True
                    else:
                        variant.active = False

                    # position
                    position = request.POST.get("position-%s" % id)
                    try:
                        variant.variant_position = int(position)
                    except ValueError:
                        variant.variant_position = 10

                variant.save()

            elif key.startswith("property"):
                # properties are marshalled as: property-variant_id|property_id
                try:
                    temp = key.split("-")[1]
                    variant_id, property_id = temp.split("|")
                    variant = Product.objects.get(pk=variant_id)
                    property = variant.get_option(property_id)
                    property.option_id = value
                except (AttributeError, IndexError, ObjectDoesNotExist):
                    continue
                else:
                    property.save()

    # Refresh variant positions
    for i, variant in enumerate(product.variants.order_by("variant_position")):
        variant.variant_position = (i+1) * 10
        variant.save()

    # Send a signal to update cache
    product_changed.send(product)

    from lfs.manage.views.product.product import selectable_products_inline
    result = simplejson.dumps({
        "properties" : manage_variants(request, product_id, as_string=True),
    })

    return HttpResponse(result)

@permission_required("manage_shop", login_url="/login/")
def edit_sub_type(request, product_id):
    """Edits the sub type of the variant with given product slug.
    """
    product = Product.objects.get(pk=product_id)

    form = DisplayTypeForm(data=request.POST)
    if form.is_valid():
        product.variants_display_type = request.POST.get("variants_display_type")
        product.save()

    # Send a signal to update cache
    product_changed.send(product)

    return HttpResponse(manage_variants(request, product_id))

def _refresh_property_positions(product_id):
    """
    """
    # Refresh positions
    for i, product_property in enumerate(ProductsPropertiesRelation.objects.filter(product=product_id)):
        product_property.position = i*2
        product_property.save()