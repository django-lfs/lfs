# django imports
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.core.fields.thumbs import ImageWithThumbsField
from lfs.core.managers import ActiveManager
from lfs.catalog.settings import PRODUCT_TYPE_CHOICES
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.catalog.settings import VARIANT, PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import VARIANTS_DISPLAY_TYPE_CHOICES
from lfs.catalog.settings import CONTENT_PRODUCTS
from lfs.catalog.settings import CONTENT_CHOICES
from lfs.catalog.settings import LIST
from lfs.catalog.settings import DELIVERY_TIME_UNIT_CHOICES
from lfs.catalog.settings import DELIVERY_TIME_UNIT_SINGULAR
from lfs.catalog.settings import DELIVERY_TIME_UNIT_HOURS
from lfs.catalog.settings import DELIVERY_TIME_UNIT_DAYS
from lfs.catalog.settings import DELIVERY_TIME_UNIT_WEEKS
from lfs.catalog.settings import DELIVERY_TIME_UNIT_MONTHS
from lfs.catalog.settings import PROPERTY_TYPE_CHOICES
from lfs.catalog.settings import PROPERTY_TEXT_FIELD
from lfs.catalog.settings import PROPERTY_SELECT_FIELD
from lfs.catalog.settings import PROPERTY_NUMBER_FIELD
from lfs.catalog.settings import PROPERTY_STEP_TYPE_CHOICES
from lfs.catalog.settings import PROPERTY_STEP_TYPE_AUTOMATIC
from lfs.catalog.settings import PROPERTY_STEP_TYPE_MANUAL_STEPS
from lfs.catalog.settings import PROPERTY_STEP_TYPE_FIXED_STEP
import lfs.catalog.utils
from lfs.tax.models import Tax

# TODO: Add attributes to the doc string.
class Category(models.Model):
    """A category is used to browse through the shop products. A category can
    have one parent category and several child categories.
    """
    name = models.CharField(_(u"Name"), max_length=50)
    slug = models.SlugField(_(u"Slug"),unique=True)
    parent = models.ForeignKey("self", verbose_name=_(u"Parent"), blank=True, null=True)

    # If selected it shows products of the sub categories within the product 
    # view. If not it shows only direct products of the category.
    show_all_products = models.BooleanField(_(u"Show all products"),default=True) 
    
    products = models.ManyToManyField("Product", verbose_name=_(u"Products"), blank=True, related_name="categories")
    short_description = models.TextField(_(u"Short description"), blank=True)
    description = models.TextField(_(u"Description"), blank=True)
    image = ImageWithThumbsField(_(u"Image"), upload_to="images", blank=True, null=True, sizes=((60, 60), (100, 100), (200, 200), (400, 400)))
    position = models.IntegerField(_(u"Position"), default=1000)
    
    static_block = models.ForeignKey("StaticBlock", verbose_name=_(u"Static block"), blank=True, null=True, related_name="categories")
    content = models.IntegerField(_(u"Content"), default=CONTENT_PRODUCTS, choices=CONTENT_CHOICES)
    active_formats = models.BooleanField(_(u"Active formats"), default=False)
    
    product_rows  = models.IntegerField(_(u"Product rows"), default=3)
    product_cols  = models.IntegerField(_(u"Product cols"), default=3)
    category_cols = models.IntegerField(_(u"Category cols"), default=3)
    
    meta_keywords = models.TextField(_(u"Meta keywords"), blank=True)
    meta_description = models.TextField(_(u"Meta description"), blank=True)
    
    class Meta:
        ordering = ("position", )
        verbose_name_plural = 'Categories'
    
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.slug)

    def get_absolute_url(self):
        """Returns the absolute_url.
        """
        return ("lfs.catalog.views.category_view", (), {"slug" : self.slug})
    get_absolute_url = models.permalink(get_absolute_url)

    @property
    def content_type(self):
        """Returns the content type of the category as lower string.
        """
        return u"category"

    def get_all_children(self):
        """Returns all child categories of the category.
        """
        def _get_all_children(category, children):
            for category in Category.objects.filter(parent=category.id):
                children.append(category)
                _get_all_children(category, children)
        
        cache_key = "category-all-children-%s" % self.id
        children = cache.get(cache_key)
        if children is not None:
            return children
            
        children = []        
        for category in Category.objects.filter(parent=self.id):
            children.append(category)
            _get_all_children(category, children)
        
        cache.set(cache_key, children)
        return children
        
    def get_children(self):
        """Returns the first level child categories.
        """
        cache_key = "category-children-%s" % self.id

        categories = cache.get(cache_key)
        if categories is not None:
            return categories
        
        categories = Category.objects.filter(parent=self.id)
        cache.set(cache_key, categories)
        
        return categories
    
    def get_format_info(self):
        """Returns format information.
        """
        if self.active_formats == True:
            return {
                "product_cols"  : self.product_cols,
                "product_rows"  : self.product_rows,
                "category_cols" : self.category_cols,
            }
        else:
            if self.parent is None:
                try:
                    # TODO: Use cache here. Maybe we need a lfs_get_object,
                    # which raise a ObjectDoesNotExist if the object does not 
                    # exist
                    from lfs.core.models import Shop
                    shop = Shop.objects.get(pk=1)
                except ObjectDoesNotExist:
                    return {
                        "product_cols": 3,
                        "product_rows" : 3,
                        "category_cols" : 3,
                    }                    
                else:
                    return {
                        "product_cols": shop.product_cols,
                        "product_rows" : shop.product_rows,
                        "category_cols" : shop.category_cols,
                    }
            else:
                return self.parent.get_format_info()

    def get_meta_keywords(self):
        """Returns the meta keywords of the catgory.
        """
        mk = self.meta_keywords.replace("<name>", self.name)
        mk = mk.replace("<short-description>", self.short_description)
        return mk
        
    def get_meta_description(self):
        """Returns the meta description of the product.
        """
        md = self.meta_description.replace("<name>", self.name)
        md = md.replace("<short-description>", self.short_description)        
        return md
    
    def get_image(self):
        """Returns the image of the category if it has none it inherits that 
        from the parent category.
        """
        if self.image:
            return self.image
        else:
            if self.parent: 
                return self.parent.get_image()

        return None
        
    def get_parents(self):
        """Returns all parent categories.
        """
        cache_key = "category-parents-%s" % self.id
        parents = cache.get(cache_key)
        if parents is not None:
            return parents

        parents = []        
        category = self.parent
        while category is not None:
            parents.append(category)
            category = category.parent
        
        cache.set(cache_key, parents)
        return parents
    
    def get_products(self):
        """Returns the direct products of the category.
        """
        cache_key = "category-products-%s" % self.id
        products = cache.get(cache_key)
        if products is not None:
            return products
        
        products = self.products.exclude(sub_type=VARIANT)
        cache.set(cache_key, products)
        
        return products
    
    def get_all_products(self):
        """Returns the direct products and all products of the sub categories
        """
        cache_key = "category-all-products-%s" % self.id
        products = cache.get(cache_key)
        if products is not None:
            return products

        categories = [self]
        categories.extend(self.get_all_children())
        
        products = lfs.catalog.models.Product.objects.distinct().filter(
            categories__in = categories).exclude(sub_type=VARIANT)
        
        cache.set(cache_key, products)
        return products
        
    def get_filtered_products(self, filters, sorting):
        """Returns products for this category filtered by passed filters sorted 
        by passed sorted
        """
        return lfs.catalog.utils.get_filtered_products_for_category(
            self, filters, sorting)
    
    def get_static_block(self):
        """Returns the static block of the category.
        """
        cache_key = "static-block-%s" % self.id
        blocks = cache.get(cache_key)
        if blocks is not None:
            return blocks
            
        block = self.static_block
        cache.set(cache_key, blocks)
        
        return block

# TODO: Add attributes to the doc string.
class Product(models.Model):
    """A product is sold within a shop.

    Parameters:
        - effective_price:
            Only for internal usage (price filtering).
    """
    # All products
    name = models.CharField(_(u"Name"), max_length=80)
    slug = models.SlugField(_(u"Slug"), unique=True, max_length=80)
    sku = models.CharField(_(u"SKU"), blank=True, max_length=30)
    price = models.FloatField(_(u"Price"), default=0.0)
    effective_price = models.FloatField(_(u"Price"), blank=True)
    short_description = models.TextField(_(u"Short description"), blank=True)
    description = models.TextField(_(u"Description"), blank=True)    
    images = generic.GenericRelation("Image", verbose_name=_(u"Images"), 
        object_id_field="content_id", content_type_field="content_type")
    
    meta_keywords = models.TextField(_(u"Meta keywords"), blank=True)
    meta_description = models.TextField(_(u"Meta description"), blank=True)
    
    related_products = models.ManyToManyField("self", verbose_name=_(u"Related products"), blank=True, null=True, 
        symmetrical=False, related_name="reverse_related_products")

    accessories = models.ManyToManyField("Product", verbose_name=_(u"Acessories"), blank=True, null=True, 
        symmetrical=False, through="ProductAccessories", 
        related_name="reverse_accessories")

    for_sale = models.BooleanField(_(u"For sale"), default=False)
    for_sale_price = models.FloatField(_(u"For sale price"), default=0.0)
    active = models.BooleanField(_(u"Active"), default=False)
    creation_date = models.DateTimeField(_(u"Creation date"), auto_now_add=True)
    
    # Stocks
    deliverable = models.BooleanField(_(u"Deliverable"), default=True)
    manual_delivery_time = models.BooleanField(_(u"Manual delivery time"), default=False)
    delivery_time = models.ForeignKey("DeliveryTime", verbose_name=_(u"Delivery time"), blank=True, null=True, related_name="products_delivery_time")
    order_time = models.ForeignKey("DeliveryTime", verbose_name=_(u"Order time"), blank=True, null=True, related_name="products_order_time")    
    ordered_at = models.DateField(_(u"Ordered at"), blank=True, null=True)
    manage_stock_amount = models.BooleanField(_(u"Manage stock amount"), default=True)
    stock_amount = models.DecimalField(_(u"Stock amount"), max_digits=3, decimal_places=1, default=0)
    
    # Dimension
    weight = models.FloatField(_(u"Weight"), default=0.0)
    height = models.FloatField(_(u"Height"), default=0.0)
    length = models.FloatField(_(u"Length"), default=0.0)
    width = models.FloatField(_(u"Width"), default=0.0)
    
    # Standard Products
    tax = models.ForeignKey(Tax, verbose_name=_(u"Tax"), blank=True, null=True)
    sub_type = models.CharField(_(u"Subtype"), 
        max_length=10, choices=PRODUCT_TYPE_CHOICES, default=STANDARD_PRODUCT)
    
    # Varianted Products
    default_variant = models.ForeignKey("self", verbose_name=_(u"Default variant"), blank=True, null=True)
    variants_display_type = models.IntegerField(_(u"Variants display type"), 
        choices=VARIANTS_DISPLAY_TYPE_CHOICES, default=LIST)
    
    # Product Variants
    parent = models.ForeignKey("self", blank=True, null=True, verbose_name=_(u"Parent"), related_name="variants")
    active_name = models.BooleanField(_(u"Active name"), default=True)
    active_sku = models.BooleanField(_(u"Active SKU"), default=True)
    active_short_description = models.BooleanField(_(u"Active short description"), default=False)
    active_description = models.BooleanField(_(u"Active description"), default=False)
    active_price = models.BooleanField(_(u"Active Price"), default=True)
    active_images = models.BooleanField(_(u"Active Images"), default=False)
    active_related_products = models.BooleanField(_(u"Active related products"), default=False)    
    active_accessories = models.BooleanField(_(u"Active accessories"), default=False)
    active_meta_description = models.BooleanField(_(u"Active meta description"), default=False)
    active_meta_keywords = models.BooleanField(_(u"Active meta keywords"), default=False)
    
    objects = ActiveManager()
    
    class Meta:
        ordering = ("name", )
        
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.slug)
    
    def save(self, force_insert=False, force_update=False):
        """Overwritten to save effective_price
        use.
        """
        if self.for_sale:
            self.effective_price = self.for_sale_price
        else:
            self.effective_price = self.price
            
        super(Product, self).save()
            
    def get_absolute_url(self):
        """Returns the absolute url of the product.
        """
        return ("lfs.catalog.views.product_view", (), {"slug" : self.slug})
    get_absolute_url = models.permalink(get_absolute_url)

    @property
    def content_type(self):
        """Returns the content type of the product as lower string.
        """
        return u"product"
    
    def decrease_stock_amount(self, amount):
        """If the stock amount is managed by LFS, it decreases stock amount by
        given amount.
        """
        if self.manage_stock_amount:
            self.stock_amount -= amount
        self.save()
            
    def get_accessories(self):
        """Returns the ProductAccessories relationship objects - not the 
        accessory (Product) objects.
        
        This is necessary to have also the default quantity of the relationship.
        """
        if self.is_variant() and not self.active_accessories:
            product = self.parent
        else:
            product = self
                        
        return ProductAccessories.objects.filter(product=product)

    def has_accessories(self):
        """Returns True if the product has accessories.
        """
        return len(self.get_accessories()) > 0
    
    def get_categories(self, with_parents=False):
        """Returns the categories of the product.
        """
        cache_key = "product-categories-%s-%s" % (self.id, with_parents)
        categories = cache.get(cache_key)

        if categories is not None:
            return categories

        if self.is_variant():
            object = self.parent
        else:
            object = self
        
        if with_parents:
            categories = []
            for category in object.categories.all():
                while category:
                    categories.append(category)
                    category = category.parent
            categories = categories
        else:
            categories = object.categories.all()
            
        cache.set(cache_key, categories)
        return categories
    
    def get_category(self):
        """Returns the first category of a product.
        """
        if self.is_variant():
            object = self.parent
        else:
            object = self
        
        try:
            return object.get_categories()[0]
        except IndexError:
            return None
        
    def get_description(self):
        """Returns the description of the product. Takes care whether the 
        product is a variant and description is active or not.
        """
        if self.is_variant() and not self.active_description:
            return self.parent.description
        else:
            return self.description

    def get_short_description(self):
        """Returns the short description of the product. Takes care whether the 
        product is a variant and short description is active or not.
        """
        if self.is_variant() and not self.active_short_description:
            return self.parent.short_description
        else:
            return self.short_description

    def get_image(self):
        """Returns the first image (the main image) of the product.
        """        
        try:
            return self.get_images()[0].image
        except IndexError:
            return None

    def get_images(self):
        """Returns all images of the product, including the main image.
        """
        cache_key = "product-images-%s" % self.id
        images = cache.get(cache_key)
        
        if images is None:
            images = []
            if self.is_variant() and not self.active_images:
                object = self.parent
            else:
                object = self
            
            images = object.images.all()
            cache.set(cache_key, images)
        
        return images
    
    def get_sub_images(self):
        """Returns all images of the product, except the main image.
        """
        return self.get_images()[1:]
    
    def get_meta_keywords(self):
        """Returns the meta keywords of the product. Takes care whether the 
        product is a variant and meta keywords are active or not.
        """
        if self.is_variant() and not self.active_meta_keywords:
            mk = self.parent.meta_keywords
        else:
            mk = self.meta_keywords
        
        mk = mk.replace("<name>", self.get_name())
        mk = mk.replace("<short-description>", self.get_short_description())
        return mk
        
    def get_meta_description(self):
        """Returns the meta description of the product. Takes care whether the 
        product is a variant and meta description are active or not.
        """
        if self.is_variant() and not self.active_meta_description:
            md = self.parent.meta_description
        else:
            md = self.meta_description
            
        md = md.replace("<name>", self.get_name())
        md = md.replace("<short-description>", self.get_short_description())
        return md

    def get_name(self):
        """Returns the name of the product. Takes care whether the product is a 
        variant and sku is active or not.
        """
        if self.is_variant() and not self.active_name:
            return self.parent.name
        else:
            return self.name

    def get_option(self, property_id):
        """Returns the id of the selected option for property with passed id.
        """
        options = cache.get("productpropertyvalue%s" % self.id)
        if options is None:
            options = {}
            for pvo in self.property_values.all():
                options[pvo.property_id] = pvo.value
            cache.set("productpropertyvalue%s" % self.id, options)
        try:
            return options[property_id]
        except KeyError:
            return None

    def get_options(self):
        """Returns the property value of a Variant in the correct 
        ordering of the properties.
        """
        cache_key = "product-property-values-%s" % self.id
        options = cache.get(cache_key)
        if options is None:
            temp = []
            for property_value in self.property_values.all():
                temp.append((property_value, property_value.property.position))
        
            # TODO: Optimize
            temp.sort(lambda a,b: cmp(a[1], b[1]))
        
            options = []
            for option in temp:
                options.append(option[0])
            
            cache.set(cache_key, options)
        
        return options

    def has_option(self, property_id, option_id):
        """Returns True if the variant has the given property / option 
        combination.
        """
        options = cache.get("productpropertyvalue%s" % self.id)
        if options is None:
            options = {}
            for pvo in self.property_values.all():                
                options[pvo.property_id] = pvo.value
            cache.set("productpropertyvalue%s" % self.id, options)
        
        try:
            return options[property_id] == str(option_id)
        except KeyError:
            return False

    def get_price(self):
        """Returns the price of the product. At the moment this is just the 
        gross price. Later this could be the net or the gross price dependent on
        selected shop options.
        """
        return self.get_price_gross()

    def get_price_gross(self):
        """Returns the real gross price of the product. Takes care whether the 
        product is for sale.
        """
        if self.is_variant() and not self.active_price:
            object = self.parent
        else:
            object = self
            
        if object.for_sale:
            return object.for_sale_price
        else:
            return object.price
        
    def get_price_net(self):
        """Returns the real net price of the product. Takes care whether the 
        product is for sale.
        """
        return self.get_price_gross() - self.get_tax()

    def get_global_properties(self):
        """Returns all global properties for the product.
        """
        properties = []
        for property_group in self.property_groups.all():
            properties.extend(property_group.properties.order_by("groupspropertiesrelation"))

        return properties
    
    def get_local_properties(self):
        """Returns local properties of the product
        """
        return self.properties.all()
    
    def get_properties(self):
        """Returns local and global properties
        """
        properties = self.get_global_properties()
        properties.extend(self.get_local_properties())
        
        return properties        
        
    def get_standard_price(self):
        """Returns always the standard price for the product. Independent
        whether the product is for sale or not. If you want the real price of 
        the product use get_price instead.
        """
        if self.is_variant() and not self.active_price:
            object = self.parent
        else:
            object = self
        
        return object.price

    def get_sku(self):
        """Returns the sku of the product. Takes care whether the product is a 
        variant and sku is active or not.
        """
        if self.is_variant() and not self.active_sku:
            return self.parent.sku
        else:
            return self.sku

    def get_tax_rate(self):
        """Returns the tax rate of the product.
        """
        if self.sub_type == VARIANT:
            if self.parent.tax is None:
                return 0.0
            else:
                return self.parent.tax.rate
        else:
            if self.tax is None:
                return 0.0
            else:
                return self.tax.rate
            
    def get_tax(self):
        """Returns the absolute tax of the product.
        """
        tax_rate = self.get_tax_rate()
        return (tax_rate/(tax_rate+100)) * self.get_price_gross()
    
    def has_related_products(self):
        """Returns True if the product has related products.
        """
        return len(self.get_related_products()) > 0
        
    def get_related_products(self):
        """Returns the related products of the product.
        """
        cache_key = "related-products-%s" % self.id
        related_products = cache.get(cache_key)

        if related_products is None:
            
            if self.is_variant() and not self.active_related_products:
                related_products = self.parent.related_products.exclude(
                    sub_type=PRODUCT_WITH_VARIANTS)
            else:
                related_products = self.related_products.exclude(
                    sub_type=PRODUCT_WITH_VARIANTS)
            
            cache.set(cache_key, related_products)

        return related_products

    def get_default_variant(self):
        """Returns the default variant.
        
        This is either a selected variant or the first added variant. If the
        product has no variants it is None.
        """
        if self.default_variant is not None:
            return self.default_variant
        else:
            try:
                return self.variants.all()[0]
            except IndexError:
                return None

    def get_variants(self):
        """Returns the variants of the product.
        """
        return self.variants.all()
        
    def has_variants(self):
        """Returns True if the product has variants.
        """
        return len(self.get_variants()) > 0
         
    def get_variant(self, options):
        """Returns the variant with the given options or None.
        
        The format of the passed properties/options must be tuple as following:

            [property.id|option.id]
            [property.id|option.id]
            ...

        NOTE: These are strings as we get the properties/options pairs out of 
        the request and it wouldn't make a lot of sense to convert them to 
        objects and back to strings.
        """
        options.sort()
        options = "".join(options)
        for variant in self.variants.all():
            temp = variant.property_values.all()
            temp = ["%s|%s" % (x.property.id, x.value) for x in temp]
            temp.sort()
            temp = "".join(temp)
            
            if temp == options:
                return variant

        return None
        
    def has_variant(self, options):
        """Returns true if a variant with given options already exists.
        """
        if self.get_variant(options) is None:
            return False
        else:
            return True
    
    def is_standard(self):
        """Returns True if product is standard product.
        """
        return self.sub_type == STANDARD_PRODUCT
    
    def is_product_with_variants(self):
        """Returns True if product is product with variants.
        """    
        return self.sub_type == PRODUCT_WITH_VARIANTS

    def is_variant(self):
        """Returns True if product is variant.
        """
        return self.sub_type == VARIANT
        
class ProductAccessories(models.Model):
    """Represents the relationship between products and accessories. 
    
    An accessory is just another product which is displayed within a product and
    which can be added to the cart together with it.
        
    Using an explicit class here to store the position of an accessory within
    a product.
    
    Attributes:
        - product
          The product of the relationship.
        - accessory
          The accessory of the relationship (which is also a product)
        - position
          The position of the accessory within the product.
        - quantity
          The proposed amount of accessories for the product.    
    """
    product = models.ForeignKey("Product", verbose_name=_(u"Product"), related_name="productaccessories_product")
    accessory = models.ForeignKey("Product", verbose_name=_(u"Acessory"), related_name="productaccessories_accessory")
    position = models.IntegerField( _(u"Position"), default=999)
    quantity = models.FloatField(_(u"Quantity"), default=1)
    
    class Meta:
        ordering = ("position", )
        verbose_name_plural = "Product accessories"        
    
    def __unicode__(self):
        return "%s -> %s" % (self.product.name, self.accessory.name)
        
    def get_price(self):
        """Returns the total price of the accessory based on the product price 
        and the quantity in which the accessory is offered.
        """
        return self.accessory.get_price() * self.quantity

class PropertyGroup(models.Model):
    """Groups product properties together.
    
    Can belong to several products, products can have several groups
    
    Attributes:
        - name
          The name of the property group.
        - products
          The assigned products of the property group.
    """
    name = models.CharField(blank=True, max_length=50)
    products = models.ManyToManyField(Product, verbose_name=_(u"Products"), related_name="property_groups")
    
    def __unicode__(self):
        return self.name

class Property(models.Model):
    """Represents a property of a product like color or size.

    A property has several ``PropertyOptions`` from which the user can choose 
    (like red, green, blue).
    
    A property belongs to exactly one group xor product.

    Parameters:
        - groups, product: 
            The group or product it belongs to. A property can belong to several 
            groups and/or to one product.
        - name:
            Is displayed within forms.
        - position: 
            The position of the property within a product.            
        - filterable:
            If True the property is used for filtered navigation.
        - display_no_results
            If True filter ranges with no products will be displayed. Otherwise
            they will be removed.
        - unit: 
            Something like cm, mm, m, etc.
        - local
            If True the property belongs to exactly one product
        - type
           char field, number field or select field
        - step
           manuel step for filtering
    """
    name = models.CharField( _(u"Name"), max_length=50)
    groups = models.ManyToManyField(PropertyGroup, verbose_name=_(u"Group"), blank=True, null=True, through="GroupsPropertiesRelation", related_name="properties")
    products = models.ManyToManyField(Product, verbose_name=_(u"Products"), blank=True, null=True, through="ProductsPropertiesRelation", related_name="properties")
    position = models.IntegerField(_(u"Position"), blank=True, null=True)
    unit = models.CharField(_(u"Unit"), blank=True, max_length=15)
    display_on_product = models.BooleanField(_(u"Display on product"), default=True)
    local = models.BooleanField(default=False)
    filterable = models.BooleanField(default=True)
    display_no_results = models.BooleanField(_(u"Display no results"), default=False)
    type = models.PositiveSmallIntegerField(_(u"Type"), choices=PROPERTY_TYPE_CHOICES, default=PROPERTY_TEXT_FIELD)
    
    step_type = models.PositiveSmallIntegerField(_(u"Step type"), choices=PROPERTY_STEP_TYPE_CHOICES, default=PROPERTY_STEP_TYPE_AUTOMATIC)
    step = models.IntegerField(_(u"Step"), blank=True, null=True)

    class Meta:
        verbose_name_plural = _(u"Properties")
        ordering = ["position"]
        
    def __unicode__(self):
        return self.name
    
    @property
    def is_select_field(self):
        return self.type == PROPERTY_SELECT_FIELD

    @property
    def is_text_field(self):
        return self.type == PROPERTY_TEXT_FIELD

    @property
    def is_number_field(self):
        return self.type == PROPERTY_NUMBER_FIELD
    
    @property
    def is_range_step_type(self):
        return self.step_type == PROPERTY_STEP_TYPE_FIXED_STEP

    @property
    def is_automatic_step_type(self):
        return self.step_type == PROPERTY_STEP_TYPE_AUTOMATIC

    @property
    def is_steps_step_type(self):
        return self.step_type == PROPERTY_STEP_TYPE_MANUAL_STEPS
        
    def is_valid_value(self, value):
        """Returns True if given value is valid for this property.
        """
        if self.is_number_field:
            try:
                float(value)
            except ValueError:
                return False
        return True

class FilterStep(models.Model):
    """A step to build filter ranges for a property.
    
    Parameters:
        - property 
          The property the Step belongs to
        - start 
          The start of the range. The end will be calculated from the start of
          the next step        
    """
    property = models.ForeignKey(Property, verbose_name=_(u"Property"), related_name="steps")
    start = models.FloatField()
    
    class Meta:
        ordering = ["start"]
        
    def __unicode__(self):
        return "%s %s" % (self.property.name, self.start)
        
class GroupsPropertiesRelation(models.Model):
    """Represents the m:n relationship between Groups and Properties.
    
    This is done via an explicit class to store the position of the property 
    within the group.
    
    Attributes:
        - group
          The property group the property belongs to.
        - property
          The property of question of the relationship.
        - position
          The position of the property within the group.
    """
    group = models.ForeignKey(PropertyGroup, verbose_name=_(u"Group"), related_name="groupproperties")
    property = models.ForeignKey(Property, verbose_name=_(u"Property"))
    position = models.IntegerField( _(u"Position"), default=999)
    
    class Meta:
        ordering = ("position", )
        unique_together = ("group", "property")

class ProductsPropertiesRelation(models.Model):
    """Represents the m:n relationship between Products and Properties.
    
    This is done via an explicit class to store the position of the property
    within the product.
    
    Attributes:
        - product
          The product of the relationship.
        - property
          The property of the relationship.
        - position
          The position of the property within the product.    
    """
    product = models.ForeignKey(Product, verbose_name=_(u"Product"), related_name="productsproperties")
    property = models.ForeignKey(Property, verbose_name=_(u"Property"))
    position = models.IntegerField( _(u"Position"), default=999)
    
    class Meta:
        ordering = ("position", )
        unique_together = ("product", "property")

class PropertyOption(models.Model):
    """Represents a choosable option of a ``Property`` like red, green, blue.
    
    A property option can have an optional price (which could change the total
    price of a product).
    
    Attributes:
        - property 
          The property to which the option belongs
        - name 
          The name of the option
        - price (Not used at the moment)
          The price for the option. This might be used for "configurable 
          products"
        - position
          The position of the option within the property
    """
    property = models.ForeignKey(Property, verbose_name=_(u"Property"), related_name="options")
    
    name = models.CharField( _(u"Name"), max_length=30)
    price = models.FloatField(_(u"Price"), blank=True, null=True, default=0.0)
    position = models.IntegerField(_(u"Position"), default=99)
    
    class Meta:
        ordering = ["position"]
    
    def __unicode__(self):
        return self.name

class ProductPropertyValue(models.Model):
    """Stores the value resp. selected option of a product/property combination.
    This is some kind of EAV.
    
    Attributes:
        - product
          The product for which the value is stored.
        - parent_id
          If the product is an variant this stores the parent id of it, if the 
          product is no variant it stores the id of the product itself. This is
          just used to calculate the filters properly.
        - property
          The property for which the value is stored.            
        - value
          The value for the product/property pair. Dependent of the property 
          type the value is either a number, a text or an id of an option.
    """
    product = models.ForeignKey(Product, verbose_name=_(u"Product"), related_name="property_values")
    parent_id = models.IntegerField(blank=True, null=True)
    property = models.ForeignKey("Property", verbose_name=_(u"Property"), related_name="property_values")
    value = models.CharField(blank=True, max_length=100)
    value_as_float = models.FloatField(blank=True, null=True)
    
    class Meta:
        unique_together = ("product", "property", "value")
        
    def __unicode__(self):
        return "%s/%s: %s" % (self.product.name, self.property.name, self.value)
        
    def save(self, force_insert=False, force_update=False):
        """Overwritten to save the parent id for variants. This is used to count
        the entries per filter. See catalog/utils/get_product_filters for more.
        """
        if self.product.is_variant():
            self.parent_id = self.product.parent.id
        else:
            self.parent_id = self.product.id
        
        try:
            float(self.value)
        except ValueError:
            pass
        else:            
            self.value_as_float = self.value
        
        super(ProductPropertyValue, self).save(force_insert, force_update)

class Image(models.Model):
    """An image with a title and several sizes. Can be part of a product or 
    category.
    
    Attributes:
        - content
          The content object it belongs to.
        - title
          The title of the image.
        - image
          The image file.
        - position
          The position of the image within the content object it belongs to.
    """
    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"), related_name="image", blank=True, null=True)
    content_id = models.PositiveIntegerField(_(u"Content id"), blank=True, null=True)
    content = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")
    
    title = models.CharField(_(u"Title"), blank=True, max_length=100)
    image = ImageWithThumbsField(_(u"Image"), upload_to="images", blank=True, null=True, sizes=((60, 60), (100, 100), (200, 200), (400, 400)))
    position = models.PositiveSmallIntegerField(_(u"Position"), default=999)

    class Meta:
        ordering = ("position", )
                
    def __unicode__(self):
        return self.title
        
class StaticBlock(models.Model):
    """A block of static HTML which can be assigned to content objects.
    
    Attributes:
        - name
          The name of the static block.
        - html 
          The static HTML of the block.
    """
    name = models.CharField(_(u"Name"), max_length=30)
    html = models.TextField( _(u"HTML"), blank=True)
    
    def __unicode__(self):
        return self.name
        
class DeliveryTime(models.Model):
    """Selectable delivery times.
    
    Attributes:
        - min
          The minimal lasting of the delivery date.
        - max
          The maximal lasting of the delivery date.
        - unit 
          The unit of the delivery date, e.g. days, months.
        - description 
          A short description for internal uses.
    """
    min = models.FloatField(_(u"Min"))
    max = models.FloatField(_(u"Max"))
    unit = models.PositiveSmallIntegerField(_(u"Unit"), choices=DELIVERY_TIME_UNIT_CHOICES, default=DELIVERY_TIME_UNIT_DAYS)
    description = models.TextField(_(u"Description"), blank=True)
    
    class Meta:
        ordering = ("min", )
        
    def __unicode__(self):
        return self.round().as_string()
        
    def __add__(self, other):
        """Adds to delivery times.
        """
        # If necessary we transform both delivery times to the same base (hours)
        if self.unit != other.unit:
            a = self.as_hours()
            b = other.as_hours()
            unit_new = DELIVERY_TIME_UNIT_HOURS
        else:
            a = self
            b = other
            unit_new = self.unit
            
        # Now we can add both
        min_new = a.min + b.min
        max_new = a.max + b.max
        unit_new = a.unit

        return DeliveryTime(min=min_new, max=max_new, unit=unit_new)
    
    @property
    def name(self):
        """Returns the name of the delivery time
        """
        return self.round().as_string()
        
    def subtract_days(self, days):
        """Substract the given days from delivery time's min and max. Takes the 
        unit into account.
        """
        if self.unit == DELIVERY_TIME_UNIT_HOURS:
            max_new = self.max - (24 * days)
            min_new = self.min - (24 * days)
        elif self.unit == DELIVERY_TIME_UNIT_DAYS:
            max_new = self.max - days
            min_new = self.min - days
        elif self.unit == DELIVERY_TIME_UNIT_WEEKS:
            max_new = self.max - (days/7.0)
            min_new = self.min - (days/7.0)
        elif self.unit == DELIVERY_TIME_UNIT_MONTHS:
            max_new = self.max - (days/30.0)
            min_new = self.min - (days/30.0)
        
        if min_new < 0:
            min_new = 0
        if max_new < 0:
            max_new = 0

        return DeliveryTime(min=min_new, max=max_new, unit=self.unit)
        
    def as_hours(self):
        """Returns the delivery time in hours.
        """
        if self.unit == DELIVERY_TIME_UNIT_HOURS:
            max = self.max
            min = self.min        
        elif self.unit == DELIVERY_TIME_UNIT_DAYS:
            max = self.max * 24
            min = self.min * 24
        elif self.unit == DELIVERY_TIME_UNIT_WEEKS:
            max = self.max * 24 * 7
            min = self.min * 24 * 7
        elif self.unit == DELIVERY_TIME_UNIT_MONTHS:
            max = self.max * 24 * 30
            min = self.min * 24 * 30
        
        return DeliveryTime(min=min, max=max, unit = DELIVERY_TIME_UNIT_HOURS)
            
    def as_days(self):
        """Returns the delivery time in days.
        """
        if self.unit == DELIVERY_TIME_UNIT_HOURS:
            min = self.min / 24
            max = self.max / 24
        elif self.unit == DELIVERY_TIME_UNIT_DAYS:
            max = self.max
            min = self.min
        elif self.unit == DELIVERY_TIME_UNIT_WEEKS:
            max = self.max * 7
            min = self.min * 7
        elif self.unit == DELIVERY_TIME_UNIT_MONTHS:
            max = self.max * 30
            min = self.min * 30
        
        return DeliveryTime(min=min, max=max, unit = DELIVERY_TIME_UNIT_DAYS)

    def as_weeks(self):
        """Returns the delivery time in weeks.
        """
        if self.unit == DELIVERY_TIME_UNIT_HOURS:
            min = self.min / (24 * 7)
            max = self.max / (24 * 7)
        elif self.unit == DELIVERY_TIME_UNIT_DAYS:
            max = self.max / 7
            min = self.min / 7
        elif self.unit == DELIVERY_TIME_UNIT_WEEKS:
            max = self.max
            min = self.min
        elif self.unit == DELIVERY_TIME_UNIT_MONTHS:
            max = self.max * 4
            min = self.min * 4
        
        return DeliveryTime(min=min, max=max, unit = DELIVERY_TIME_UNIT_WEEKS)

    def as_months(self):
        """Returns the delivery time in months.
        """
        if self.unit == DELIVERY_TIME_UNIT_HOURS:
            min = self.min / (24 * 30)
            max = self.max / (24 * 30)
        elif self.unit == DELIVERY_TIME_UNIT_DAYS:
            max = self.max / 30
            min = self.min / 30
        elif self.unit == DELIVERY_TIME_UNIT_WEEKS:
            max = self.max / 4
            min = self.min / 4
        elif self.unit == DELIVERY_TIME_UNIT_MONTHS:
            max = self.max
            min = self.min
        
        return DeliveryTime(min=min, max=max, unit = DELIVERY_TIME_UNIT_MONTHS)
    
    def as_reasonable_unit(self):
        """Returns the delivery time as reasonable unit based on the max hours.

        This is used to show the delivery time to the shop customer.
        """
        delivery_time = self.as_hours()

        if delivery_time.max > 1440:               # > 2 months
            return delivery_time.as_months()        
        elif delivery_time.max > 168:              # > 1 week
            return delivery_time.as_weeks()     
        elif delivery_time.max > 48:               # > 2 days
            return delivery_time.as_days()
        else:
            return delivery_time
            
    def as_string(self):
        """Returns the delivery time as string.
        """
        if self.min == 0:
            self.min = self.max
            
        if self.min == self.max:
            if self.min == 1:
                unit = DELIVERY_TIME_UNIT_SINGULAR[self.unit]
            else:
                unit = self.get_unit_display()
                
            return "%s %s" % (self.min, unit)
        else:
            return "%s-%s %s" % (self.min, self.max, self.get_unit_display())
                
    def round(self):
        """Rounds the min/max of the delivery time to an integer and returns a 
        new DeliveryTime object.
        """        
        min = int("%.0f" % (self.min + 0.001))
        max = int("%.0f" % (self.max + 0.001))
        
        return DeliveryTime(min=min, max=max, unit=self.unit)