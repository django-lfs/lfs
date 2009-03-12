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

from lfs.tax.models import Tax

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
        keywords = self.meta_keywords.replace("<title>", self.name)
        return keywords
        
    def get_meta_description(self):
        """Returns the meta description of the product.
        """
        return self.meta_description
    
    def get_image(self):
        """Returns the image of the category if ít has none it inherits that 
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
        """Returns the products of the category.
        """
        cache_key = "category-products-%s" % self.id
        products = cache.get(cache_key)
        if products is not None:
            return products
        
        products = self.products.exclude(sub_type=VARIANT)
        cache.set(cache_key, products)
        
        return products

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

class Product(models.Model):
    """A product is sold within a shop.
    """
    # All products
    name = models.CharField(_(u"Name"), max_length=80)
    slug = models.SlugField(_(u"Slug"), unique=True, max_length=80)
    sku = models.CharField(_(u"SKU"), blank=True, max_length=30)
    price = models.FloatField(_(u"Price"), default=0.0)
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
    properties = models.ManyToManyField("Property", verbose_name=_(u"Properties"), through="ProductProperties")
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
            keywords = self.parent.meta_keywords
        else:
            keywords = self.meta_keywords
        
        keywords = keywords.replace("<title>", self.get_name())
        return keywords
        
    def get_meta_description(self):
        """Returns the meta description of the product. Takes care whether the 
        product is a variant and meta description are active or not.
        """
        if self.is_variant() and not self.active_meta_description:
            return self.parent.meta_description
        else:
            return self.meta_description

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
        options = cache.get("productvariantoptions%s" % self.id)
        if options is None:
            options = {}
            for pvo in self.productvariantoption_set.all():
                options[pvo.property_id] = pvo.option_id
            cache.set("productvariantoptions%s" % self.id, options)
        try:
            return options[property_id]
        except KeyError:
            return None

    def get_options(self):
        """Returns the property/option pairs of a varianted product in the 
        correct ordering of the properties.
        """
        options = cache.get("productvariantoptions_sorted%s" % self.id)
        if options is None:
            temp = []
            for option in self.productvariantoption_set.all():
                product_property = ProductProperties.objects.get(product=self.parent, property=option.property)
                temp.append((option, product_property.position))
        
            # TODO: Optimize
            temp.sort(lambda a,b: cmp(a[1], b[1]))
        
            options = []
            for option in temp:
                options.append(option[0])
            
            cache.set("productvariantoptions_sorted%s" % self.id, options)
            
        return options

    def has_option(self, property_id, option_id):
        """Returns True if the variant has the given property / option 
        combination.
        """
        options = cache.get("productvariantoptions%s" % self.id)
        if options is None:
            options = {}
            for pvo in self.productvariantoption_set.all():
                options[pvo.property_id] = pvo.option_id
            cache.set("productvariantoptions%s" % self.id, options)
            
        try:
            return options[property_id] == option_id
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
            temp = variant.productvariantoption_set.all()
            temp = ["%s|%s" % (x.property.id, x.option.id) for x in temp]
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
    
    def is_standard_product(self):
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
    """
    product = models.ForeignKey("Product", verbose_name=_(u"Product"), related_name="productaccessories_product")
    accessory = models.ForeignKey("Product", verbose_name=_(u"Acessory"), related_name="productaccessories_accessory")
    position = models.IntegerField( _(u"Position"), default=999)
    quantity = models.FloatField(_(u"Quantity"), default=1)
    
    class Meta:
        ordering = ("position", )
        verbose_name_plural = "ProductAccessories"        
    
    def __unicode__(self):
        return "%s -> %s" % (self.product.name, self.accessory.name)
        
    def get_price(self):
        """Returns the total price of the accessory based on the product price 
        and the quantity in which the accessory is offered.
        """
        return self.accessory.get_price() * self.quantity
        
class ProductProperties(models.Model):
    """Represents the relationship between products and properties. 
    
    Using an additional class here to store the position of a property within 
    a product.
    """
    product = models.ForeignKey("Product", verbose_name=_(u"Product"))
    property = models.ForeignKey("Property", verbose_name=_(u"Property"))
    position = models.IntegerField(_(u"Position"), blank=True, null=True)

    class Meta:
        ordering = ("position", )
        verbose_name_plural = "ProductProperties"
        
    def __unicode__(self):
        return "%s -> %s" % (self.product.name, self.property.name)
    
class ProductVariantOption(models.Model):
    """Represents the unique property/option combination for a ProductVariant``
    variant.
    
    A ``ProductVariant`` can have several such combinations.
    """
    product = models.ForeignKey(Product, verbose_name=_(u"Product"))
    property = models.ForeignKey("Property", verbose_name=_(u"Property"))
    option = models.ForeignKey("PropertyOption", verbose_name=_(u"Option"))
    
    def __unicode__(self):
        return "%s - %s" % (self.property.name, self.option.name)

class Property(models.Model):
    """Represents a property of a product like color or size.
    
    A property has several ``PropertyOptions`` from which the user can choose 
    (like red, green, blue).
    """
    name = models.CharField( _(u"Name"), max_length=30)

    class Meta:
        verbose_name_plural = "Properties"

    def __unicode__(self):
        return self.name
    
class PropertyOption(models.Model):
    """Represents a choosable option of a ``Property`` like red, green, blue.
    
    A property option can have a price (which could change the total price of 
    a product).
    """
    property = models.ForeignKey(Property, verbose_name=_(u"Property"))
    
    name = models.CharField( _(u"Name"), max_length=30)
    price = models.FloatField(_(u"Price"), blank=True, null=True, default=0.0)
    position = models.IntegerField(_(u"Position"), blank=True, null=True)
    
    class Meta:
        ordering = ("position", )
    
    def __unicode__(self):
        return self.name
        
class Image(models.Model):
    """An image with a title and several sizes. Can be part of a product or 
    category.
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
    """
    name = models.CharField(_(u"Name"), max_length=30)
    html = models.TextField( _(u"HTML"), blank=True)
    
    def __unicode__(self):
        return self.name
        
class DeliveryTime(models.Model):
    """Selectable delivery times.
    """
    min = models.FloatField(_(u"Min"))
    max = models.FloatField(_(u"Max"))
    unit = models.PositiveSmallIntegerField(_(u"Unit"), choices=DELIVERY_TIME_UNIT_CHOICES, default=DELIVERY_TIME_UNIT_DAYS)
    
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