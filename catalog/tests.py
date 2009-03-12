# django imports
from django.core.urlresolvers import reverse
from django.test import TestCase

# lfs imports
from lfs.catalog.settings import CONTENT_CATEGORIES
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS, VARIANT
from lfs.catalog.settings import DELIVERY_TIME_UNIT_HOURS
from lfs.catalog.settings import DELIVERY_TIME_UNIT_WEEKS
from lfs.catalog.settings import DELIVERY_TIME_UNIT_DAYS
from lfs.catalog.settings import DELIVERY_TIME_UNIT_MONTHS
from lfs.catalog.models import Category
from lfs.catalog.models import DeliveryTime
from lfs.catalog.models import Image
from lfs.catalog.models import Product
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption
from lfs.catalog.models import ProductAccessories
from lfs.catalog.models import ProductProperties
from lfs.catalog.models import ProductVariantOption
from lfs.core.signals import product_changed
from lfs.tax.models import Tax

class ViewsTestCase(TestCase):
    """Tests the views of the lfs.catalog.
    """
    fixtures = ['lfs_shop.xml']

    def setUp(self):
        """
        """
        self.c1 = Category.objects.create(name="Category 1", slug="category-1")
        self.p1 = Product.objects.create(name="Product 1", slug="product-1", sub_type=PRODUCT_WITH_VARIANTS)
        
        # Create a property with two options
        color = Property.objects.create(name="Color")
        red = PropertyOption.objects.create(name="Red", property=color)
        green = PropertyOption.objects.create(name="Green", property=color)
        
        # Associate the product with the property
        ProductProperties.objects.create(product=self.p1, property=color)
        
        # Add a variant with color = red
        self.v1 = Product.objects.create(name="Variant 1", slug="variant-1", sub_type=VARIANT, parent=self.p1)
        ProductVariantOption.objects.create(product=self.v1, property=color, option=red)
        
    def test_set_sorting(self):
        """Tests setting and deleting of the sorting session.
        """
        url = reverse("lfs_catalog_set_sorting")
        
        # At the beginning there is no sorting stored
        self.failIf(self.client.session.has_key("sorting"))

        # Empty string shouldn't raise an error
        self.client.post(url, {'sorting': ''})
        
        # Post a sorting
        self.client.post(url, {'sorting': '-name'})
        self.assertEqual(self.client.session.get("sorting"), "-name")

        # Post another sorting        
        self.client.post(url, {'sorting': '+price'})
        self.assertEqual(self.client.session.get("sorting"), "+price")

        # Empty string should delete session sorting key
        self.client.post(url, {'sorting': ''})
        self.failIf(self.client.session.has_key("sorting"))

    def test_category_view(self):
        """Tests whether the right template is used for products and sub 
        category view of a category.
        """
        url = reverse("lfs_category", kwargs={"slug": "category-1", "start": 0})
        response = self.client.get(url, {'sorting': ''})
        templates = [t.name for t in response.template]        
                
        # By default the products of a category should be displayed
        self.failIf("catalog/category_products.html" not in templates)
        self.failIf("catalog/category_categories.html" in templates)
        
        # Switch to categories within a category
        self.c1.content = CONTENT_CATEGORIES
        self.c1.save()

        response = self.client.get(url, {'sorting': ''})
        templates = [t.name for t in response.template]        
        
        # Now the categories template should be used
        self.failIf("catalog/category_products.html" in templates)
        self.failIf("catalog/category_categories.html" not in templates)
        
    def test_product_form_dispatcher(self):
        """Tests the product dispatcher. The product dispatcher decides where to
        go after the product form (for shop customers) has been submitted. These
        can either be a variant or the add-to-cart view.
        """
        url = reverse("lfs_product_dispatcher")
        
        # Add the variant to cart
        response = self.client.post(url, {"add-to-cart" : 1, "product_id" : self.v1.id})
        
        # Select the default variant
        response = self.client.post(url, {"product_id" : self.p1.id})
        
        # Select the variant color = red
        response = self.client.post(url, {"product_id" : self.p1.id, "property_1"  : "1" })

class DeliveryTimeTestCase(TestCase):
    """Tests attributes and methods of DeliveryTime objects.
    """
    def setUp(self):
        """
        """
        self.dm1 = DeliveryTime.objects.create(min=1.0, max=3.0, unit=DELIVERY_TIME_UNIT_HOURS)
        self.dm2 = DeliveryTime.objects.create(min=1.0, max=3.0, unit=DELIVERY_TIME_UNIT_DAYS)
        self.dm3 = DeliveryTime.objects.create(min=1.0, max=3.0, unit=DELIVERY_TIME_UNIT_WEEKS)
        self.dm4 = DeliveryTime.objects.create(min=1.0, max=3.0, unit=DELIVERY_TIME_UNIT_MONTHS)
        
    def test_as_hours(self):
        """
        """
        self.assertEqual(self.dm1.as_hours().min, 1)
        self.assertEqual(self.dm1.as_hours().max, 3)
        self.assertEqual(self.dm2.as_hours().min, 24)
        self.assertEqual(self.dm2.as_hours().max, 72)
        self.assertEqual(self.dm3.as_hours().min, 168)
        self.assertEqual(self.dm3.as_hours().max, 504)
        self.assertEqual(self.dm4.as_hours().min, 720)
        self.assertEqual(self.dm4.as_hours().max, 2160)

    def test_as_days(self):
        """
        """
        self.assertEqual(self.dm1.as_days().min, 1.0/24)
        self.assertEqual(self.dm1.as_days().max, 3.0/24)
        self.assertEqual(self.dm2.as_days().min, 1)
        self.assertEqual(self.dm2.as_days().max, 3)
        self.assertEqual(self.dm3.as_days().min, 7)
        self.assertEqual(self.dm3.as_days().max, 21)
        self.assertEqual(self.dm4.as_days().min, 30)
        self.assertEqual(self.dm4.as_days().max, 90)

    def test_as_weeks(self):
        """
        """
        self.assertEqual(self.dm1.as_weeks().min, 1.0/(24*7))
        self.assertEqual(self.dm1.as_weeks().max, 3.0/(24*7))
        self.assertEqual(self.dm2.as_weeks().min, 1.0/7)
        self.assertEqual(self.dm2.as_weeks().max, 3.0/7)
        self.assertEqual(self.dm3.as_weeks().min, 1)
        self.assertEqual(self.dm3.as_weeks().max, 3)
        self.assertEqual(self.dm4.as_weeks().min, 4)
        self.assertEqual(self.dm4.as_weeks().max, 12)

    def test_as_month(self):
        """
        """
        self.assertEqual(self.dm1.as_months().min, 1.0/(24*30))
        self.assertEqual(self.dm1.as_months().max, 3.0/(24*30))
        self.assertEqual(self.dm2.as_months().min, 1.0/30)
        self.assertEqual(self.dm2.as_months().max, 3.0/30)
        self.assertEqual(self.dm3.as_months().min, 1.0/4)
        self.assertEqual(self.dm3.as_months().max, 3.0/4)
        self.assertEqual(self.dm4.as_months().min, 1)
        self.assertEqual(self.dm4.as_months().max, 3)

    def test_as_reasonable_unit(self):
        """
        """
        d = DeliveryTime(min=24, max=48, unit=DELIVERY_TIME_UNIT_HOURS)
        d = d.as_reasonable_unit()
        self.assertEqual(d.min, 24)
        self.assertEqual(d.max, 48)
        self.assertEqual(d.unit, DELIVERY_TIME_UNIT_HOURS)

        d = DeliveryTime(min=96, max=120, unit=DELIVERY_TIME_UNIT_HOURS)
        d = d.as_reasonable_unit()
        self.assertEqual(d.min, 4)
        self.assertEqual(d.max, 5)
        self.assertEqual(d.unit, DELIVERY_TIME_UNIT_DAYS)
        
        d = DeliveryTime(min=7, max=14, unit=DELIVERY_TIME_UNIT_DAYS)
        d = d.as_reasonable_unit()
        self.assertEqual(d.min, 1)
        self.assertEqual(d.max, 2)
        self.assertEqual(d.unit, DELIVERY_TIME_UNIT_WEEKS)

        d = DeliveryTime(min=6, max=10, unit=DELIVERY_TIME_UNIT_WEEKS)
        d = d.as_reasonable_unit()
        self.assertEqual(d.min, 1)
        self.assertEqual(d.max, 2)
        self.assertEqual(d.unit, DELIVERY_TIME_UNIT_MONTHS)
        
    def test_as_string(self):
        """
        """
        # Hour
        d = DeliveryTime(min=0, max=1, unit=DELIVERY_TIME_UNIT_HOURS)
        self.assertEqual(d.as_string(), "1 hour")
        
        d = DeliveryTime(min=1, max=1, unit=DELIVERY_TIME_UNIT_HOURS)
        self.assertEqual(d.as_string(), "1 hour")

        d = DeliveryTime(min=2, max=2, unit=DELIVERY_TIME_UNIT_HOURS)
        self.assertEqual(d.as_string(), "2 hours")

        d = DeliveryTime(min=2, max=3, unit=DELIVERY_TIME_UNIT_HOURS)
        self.assertEqual(d.as_string(), "2-3 hours")

        # Days        
        d = DeliveryTime(min=0, max=1, unit=DELIVERY_TIME_UNIT_DAYS)
        self.assertEqual(d.as_string(), "1 day")
        
        d = DeliveryTime(min=1, max=1, unit=DELIVERY_TIME_UNIT_DAYS)
        self.assertEqual(d.as_string(), "1 day")

        d = DeliveryTime(min=2, max=2, unit=DELIVERY_TIME_UNIT_DAYS)
        self.assertEqual(d.as_string(), "2 days")

        d = DeliveryTime(min=2, max=3, unit=DELIVERY_TIME_UNIT_DAYS)
        self.assertEqual(d.as_string(), "2-3 days")
        
        # Weeks        
        d = DeliveryTime(min=0, max=1, unit=DELIVERY_TIME_UNIT_WEEKS)
        self.assertEqual(d.as_string(), "1 week")
        
        d = DeliveryTime(min=1, max=1, unit=DELIVERY_TIME_UNIT_WEEKS)
        self.assertEqual(d.as_string(), "1 week")

        d = DeliveryTime(min=2, max=2, unit=DELIVERY_TIME_UNIT_WEEKS)
        self.assertEqual(d.as_string(), "2 weeks")

        d = DeliveryTime(min=2, max=3, unit=DELIVERY_TIME_UNIT_WEEKS)
        self.assertEqual(d.as_string(), "2-3 weeks")
        
        # Months
        d = DeliveryTime(min=0, max=1, unit=DELIVERY_TIME_UNIT_MONTHS)
        self.assertEqual(d.as_string(), "1 month")
        
        d = DeliveryTime(min=1, max=1, unit=DELIVERY_TIME_UNIT_MONTHS)
        self.assertEqual(d.as_string(), "1 month")

        d = DeliveryTime(min=2, max=2, unit=DELIVERY_TIME_UNIT_MONTHS)
        self.assertEqual(d.as_string(), "2 months")

        d = DeliveryTime(min=2, max=3, unit=DELIVERY_TIME_UNIT_MONTHS)
        self.assertEqual(d.as_string(), "2-3 months")
                
    def test_add(self):
        """Tests the adding of delivery times.
        """
        # ### hours
                
        # hours + hours
        result = self.dm1 + self.dm1
        self.assertEqual(result.min, 2)
        self.assertEqual(result.max, 6)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)
        
        # hours + days
        result = self.dm1 + self.dm2
        self.assertEqual(result.min, 25)
        self.assertEqual(result.max, 75)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)
        
        # hours + weeks
        result = self.dm1 + self.dm3
        self.assertEqual(result.min, 169)
        self.assertEqual(result.max, 507)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)
        
        # hours + month
        result = self.dm1 + self.dm4
        self.assertEqual(result.min, 721)
        self.assertEqual(result.max, 2163)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)
                
        # ### Days
        
        # days + hours
        result = self.dm2 + self.dm1
        self.assertEqual(result.min, 25)
        self.assertEqual(result.max, 75)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)
        
        # days + days
        result = self.dm2 + self.dm2
        self.assertEqual(result.min, 2)
        self.assertEqual(result.max, 6)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_DAYS)

        # days + weeks
        result = self.dm2 + self.dm3
        self.assertEqual(result.min, 192)
        self.assertEqual(result.max, 576)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)
        
        # days + months
        result = self.dm2 + self.dm4
        self.assertEqual(result.min, 744)
        self.assertEqual(result.max, 2232)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)
        
        # ### Weeks
        
        # weeks + hours
        result = self.dm3 + self.dm1
        self.assertEqual(result.min, 169)
        self.assertEqual(result.max, 507)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)
        
        # weeks + days
        result = self.dm3 + self.dm2
        self.assertEqual(result.min, 192)
        self.assertEqual(result.max, 576)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)

        # weeks + weeks
        result = self.dm3 + self.dm3
        self.assertEqual(result.min, 2)
        self.assertEqual(result.max, 6)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_WEEKS)

        # weeks + months
        result = self.dm3 + self.dm4
        self.assertEqual(result.min, 888)
        self.assertEqual(result.max, 2664)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)

        # ### Months
        
        # months + hours
        result = self.dm4 + self.dm1
        self.assertEqual(result.min, 721)
        self.assertEqual(result.max, 2163)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)
        
        # months + days
        result = self.dm4 + self.dm2
        self.assertEqual(result.min, 744)
        self.assertEqual(result.max, 2232)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)

        # months + weeks
        result = self.dm4 + self.dm3
        self.assertEqual(result.min, 888)
        self.assertEqual(result.max, 2664)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_HOURS)

        # months + months
        result = self.dm4 + self.dm4
        self.assertEqual(result.min, 2)
        self.assertEqual(result.max, 6)
        self.assertEqual(result.unit, DELIVERY_TIME_UNIT_MONTHS)

    def test_round(self):
        """
        """
        # round down
        d = DeliveryTime(min=1.1, max=2.1, unit=DELIVERY_TIME_UNIT_HOURS)
        d = d.round()        
        self.assertEqual(d.min, 1)
        self.assertEqual(d.max, 2)
        self.assertEqual(d.unit, DELIVERY_TIME_UNIT_HOURS)

        # .5 should be rounded up
        d = DeliveryTime(min=1.5, max=2.5, unit=DELIVERY_TIME_UNIT_HOURS)
        d = d.round()        
        self.assertEqual(d.min, 2)
        self.assertEqual(d.max, 3)
        self.assertEqual(d.unit, DELIVERY_TIME_UNIT_HOURS)

        # round up
        d = DeliveryTime(min=1.6, max=2.6, unit=DELIVERY_TIME_UNIT_HOURS)
        d = d.round()        
        self.assertEqual(d.min, 2)
        self.assertEqual(d.max, 3)
        self.assertEqual(d.unit, DELIVERY_TIME_UNIT_HOURS)

    def test_subtract_days(self):
        """
        """
        d = DeliveryTime(min=48, max=72, unit=DELIVERY_TIME_UNIT_HOURS)
        d = d.subtract_days(1)        
        self.assertEqual(d.min, 24)
        self.assertEqual(d.max, 48)
        self.assertEqual(d.unit, DELIVERY_TIME_UNIT_HOURS)

        d = DeliveryTime(min=5, max=6, unit=DELIVERY_TIME_UNIT_DAYS)
        d = d.subtract_days(1)        
        self.assertEqual(d.min, 4)
        self.assertEqual(d.max, 5)
        self.assertEqual(d.unit, DELIVERY_TIME_UNIT_DAYS)

        d = DeliveryTime(min=5, max=6, unit=DELIVERY_TIME_UNIT_WEEKS)
        d = d.subtract_days(7)        
        self.assertEqual(d.min, 4)
        self.assertEqual(d.max, 5)
        self.assertEqual(d.unit, DELIVERY_TIME_UNIT_WEEKS)

        d = DeliveryTime(min=5, max=6, unit=DELIVERY_TIME_UNIT_MONTHS)
        d = d.subtract_days(30)        
        self.assertEqual(d.min, 4)
        self.assertEqual(d.max, 5)
        self.assertEqual(d.unit, DELIVERY_TIME_UNIT_MONTHS)
        
class ProductTestCase(TestCase):
    """Tests attributes and methods of Products
    """
    def setUp(self):
        """
        """
        # Create a tax
        self.t1 = Tax.objects.create(rate=19.0)
        
        # A product with properties and variants
        self.p1 = Product.objects.create(
            name=u"Product 1", 
            slug=u"product-1",
            sku=u"SKU P1",
            description=u"This is the description of product 1", 
            meta_description=u"This is the meta description of product 1", 
            meta_keywords=u"This is the meta keywords of product 1",
            sub_type=PRODUCT_WITH_VARIANTS,
            tax=self.t1,
            price=1.0,
            for_sale_price=0.5,
            stock_amount=2)
            
        # Products without properties and variants
        self.p2 = Product.objects.create(name=u"Product 2", slug=u"product-2")
        self.p3 = Product.objects.create(name=u"Product 3", slug=u"product-3")
        
        # Create a size property with two options
        self.size = size = Property.objects.create(name="Size")
        self.l = l = PropertyOption.objects.create(name="L", property=size)
        self.m = m = PropertyOption.objects.create(name="M", property=size)
        
        # Create a color property with two options
        self.color = color = Property.objects.create(name="Color")
        self.red = red = PropertyOption.objects.create(name="Red", property=color)
        self.green = green = PropertyOption.objects.create(name="Green", property=color)
        
        # Associate the product with the properties
        ProductProperties.objects.create(product=self.p1, property=color)
        ProductProperties.objects.create(product=self.p1, property=size)
        
        # Add a variant with color = red, size = m
        self.v1 = Product.objects.create(
            name=u"Variant 1", 
            slug=u"variant-1",
            sku=u"SKU V1",
            description=u"This is the description of variant 1", 
            meta_description=u"This is the meta description of variant 1", 
            meta_keywords=u"This is the meta keywords of variant 1",
            sub_type=VARIANT, 
            price=2.0,
            for_sale_price = 1.5,
            parent=self.p1)
            
        self.pvo_color_red = ProductVariantOption.objects.create(product=self.v1, property=color, option=red)
        self.pvo_size_m = ProductVariantOption.objects.create(product=self.v1, property=size, option=m)

        # Add a variant with color = green, size = l
        self.v2 = Product.objects.create(name="Variant 2", slug="variant-2", sub_type=VARIANT, parent=self.p1)
        self.pvo_color_green = ProductVariantOption.objects.create(product=self.v2, property=color, option=green)
        self.pvo_size_l = ProductVariantOption.objects.create(product=self.v2, property=size, option=l)

        # Add related products to p1
        self.p1.related_products.add(self.p2, self.p3)
        self.p1.save()

        # Assign accessories to products
        self.pa_1_2 = ProductAccessories.objects.create(product=self.p1, accessory=self.p2, position=1)
        self.pa_1_3 = ProductAccessories.objects.create(product=self.p1, accessory=self.p3, position=2)

        self.pa_2_1 = ProductAccessories.objects.create(product=self.p2, accessory=self.p1, position=1)
        self.pa_2_3 = ProductAccessories.objects.create(product=self.p2, accessory=self.p3, position=2)

        self.pa_3_1 = ProductAccessories.objects.create(product=self.p3, accessory=self.p1, position=1)
        self.pa_3_2 = ProductAccessories.objects.create(product=self.p3, accessory=self.p2, position=2)

        # Create some categories
        self.c1 = Category.objects.create(name="Category 1", slug="category-1")
        self.c11 = Category.objects.create(name="Category 11", slug="category-11", parent=self.c1)
        self.c111 = Category.objects.create(name="Category 111", slug="category-111", parent=self.c11)
        self.c2 = Category.objects.create(name="Category 2", slug="category-2")
        
        # Assign products to categories. Note: p2 has two top level categories
        self.c111.products = (self.p1, self.p2)
        self.c2.products = (self.p2, )

        # Create some dummy images
        self.i1 = Image.objects.create(title="Image 1", position=1)
        self.i2 = Image.objects.create(title="Image 2", position=2)
        self.i3 = Image.objects.create(title="Image 3", position=3)
        self.i4 = Image.objects.create(title="Image 4", position=1)
        self.i5 = Image.objects.create(title="Image 5", position=2)
        
        # Assign images to product
        self.p1.images.add(self.i1, self.i2, self.i3)

        # Assign images to variant
        self.v1.images.add(self.i4, self.i5)
    
    def test_defaults(self):
        """Tests the default value after a product has been created
        """
        self.assertEqual(1, 0)
        
    def test_decrease_stock_amount(self):
        """Tests the decreasing of the stock amount
        """
        # By default the stock amount is managed by LFS and the stock amount 
        # is decrease when a product has been sold.
        self.p1.decrease_stock_amount(1)
        self.assertEqual(self.p1.stock_amount, 1)

        # Now we remove the management of the stock amount
        self.p1.manage_stock_amount = False
        self.p1.save()
        
        # We try to decrease the stock amount ...
        self.p1.decrease_stock_amount(1)
        
        # ... but as the stock amount is not managed by LFS any more we have 
        # still 1 in the stock.
        self.assertEqual(self.p1.stock_amount, 1)

    def test_get_accessories(self):
        """Tests the get_accessories method. Takes into account the retrieving
        of accessories in the correct order. Tests also the inheritance of
        accessories for variant.
        """        
        names = [a.accessory.name for a in self.p1.get_accessories()]
        self.assertEqual(names, ["Product 2", "Product 3"])

        # By default the variant has the same accessory as the parent product        
        names = [a.accessory.name for a in self.v1.get_accessories()]
        self.assertEqual(names, ["Product 2", "Product 3"])
        
        # Now we change the position
        self.pa_1_2.position = 3
        self.pa_1_2.save()
        
        # The order has been changed
        names = [a.accessory.name for a in self.p1.get_accessories()]
        self.assertEqual(names, ["Product 3", "Product 2"])

        # Also for the variant of course
        names = [a.accessory.name for a in self.v1.get_accessories()]
        self.assertEqual(names, ["Product 3", "Product 2"])
        
        # Now we assign own accessories for the variant
        self.v1.active_accessories = True
        self.v1.save()
        
        # We assign the same products but in another order
        ProductAccessories.objects.create(product=self.v1, accessory=self.p2, position=1)
        ProductAccessories.objects.create(product=self.v1, accessory=self.p3, position=2)
        
        names = [a.accessory.name for a in self.v1.get_accessories()]
        self.assertEqual(names, ["Product 2", "Product 3"])
        
        # Now we test quickly the other products
        names = [a.accessory.name for a in self.p2.get_accessories()]
        self.assertEqual(names, ["Product 1", "Product 3"])
        
        names = [a.accessory.name for a in self.p3.get_accessories()]
        self.assertEqual(names, ["Product 1", "Product 2"])
    
    def test_get_categories(self):
        """
        """
        # Get categories without parents (implicit)
        names = [c.name for c in self.p1.get_categories()]
        self.assertEqual(names, ["Category 111"])
        
        # Get categories without parents (explicit)
        names = [c.name for c in self.p1.get_categories(with_parents=False)]
        self.assertEqual(names, ["Category 111"])

        # Get categories with parents
        names = [c.name for c in self.p1.get_categories(with_parents=True)]
        self.assertEqual(names, ["Category 111", "Category 11", "Category 1"])
        
        ###  Now the same for Product 2 which has two categories
        # Get categories without parents (implicit)
        names = [c.name for c in self.p2.get_categories()]
        self.assertEqual(names, ["Category 111", "Category 2"])
        
        # Get categories without parents (explicit)
        names = [c.name for c in self.p2.get_categories(with_parents=False)]
        self.assertEqual(names, ["Category 111", "Category 2"])

        # Get categories with parents
        names = [c.name for c in self.p2.get_categories(with_parents=True)]
        self.assertEqual(names, ["Category 111", "Category 11", "Category 1", "Category 2"])
    
    def test_get_description(self):
        """
        """
        # Test product
        self.assertEqual(self.p1.get_description(), u"This is the description of product 1")
        
        # Test variant. By default the description of a variant is inherited 
        # from parent product.
        self.assertEqual(self.v1.get_description(), u"This is the description of product 1")
        
        # Now we switch to active description.
        self.v1.active_description = True
        self.v1.save()
        
        # Now we get the description of the variant
        self.assertEqual(self.v1.get_description(), u"This is the description of variant 1")

    def test_get_image(self):
        """
        """
        image = self.p1.get_image()
        self.assertEqual(image.instance.title, "Image 1")
        
        # We change the position of the image
        self.i1.position = 5
        self.i1.save()
        
        # We have to sent product_changed in order to refresh cache
        product_changed.send(self.p1)
        
        # We get another main images
        image = self.p1.get_image()
        self.assertEqual(image.instance.title, "Image 2")
        
        # By default variants inherit images of parent product
        image = self.v1.get_image()
        self.assertEqual(image.instance.title, "Image 2")
        
        # Switch to own images
        self.v1.active_images = True
        self.v1.save()
        
        # We get the image of the variant now
        image = self.v1.get_image()
        self.assertEqual(image.instance.title, "Image 4")

    def test_get_images(self):
        """
        """
        titles = [i.title for i in self.p1.get_images()]
        self.assertEqual(titles, ["Image 1", "Image 2", "Image 3"])

        # We change the position of the image 
        self.i1.position = 5
        self.i1.save()
        
        # We have to sent product_changed in order to refresh cache
        product_changed.send(self.p1)
        
        # We get another order of the images
        titles = [i.title for i in self.p1.get_images()]
        self.assertEqual(titles, ["Image 2", "Image 3", "Image 1"])

        # By default variants inherit images of parent product
        titles = [i.title for i in self.v1.get_images()]
        self.assertEqual(titles, ["Image 2", "Image 3", "Image 1"])

        # Switch to own images
        self.v1.active_images = True
        self.v1.save()

        # We get the images of the variant now        
        titles = [i.title for i in self.v1.get_images()]
        self.assertEqual(titles, ["Image 4", "Image 5"])

    def test_get_sub_images(self):
        """
        """
        titles = [i.title for i in self.p1.get_sub_images()]
        self.assertEqual(titles, ["Image 2", "Image 3"])

        # We change the position of the image 
        self.i1.position = 5
        self.i1.save()
        
        # We have to sent product_changed in order to refresh cache
        product_changed.send(self.p1)

        # We get another order of the images
        titles = [i.title for i in self.p1.get_sub_images()]
        self.assertEqual(titles, ["Image 3", "Image 1"])

        # By default variants inherit images of parent product
        titles = [i.title for i in self.p1.get_sub_images()]
        self.assertEqual(titles, ["Image 3", "Image 1"])

        # Switch to own images
        self.v1.active_images = True
        self.v1.save()

        # We get the images of the variant now
        titles = [i.title for i in self.v1.get_sub_images()]
        self.assertEqual(titles, ["Image 5"])
        
    def test_get_meta_keywords(self):
        """
        """
        # Test product
        self.assertEqual(self.p1.get_meta_keywords(), u"This is the meta keywords of product 1")
        
        # Test variant. By default the meta keywords of a variant is inherited 
        # from parent product.
        self.assertEqual(self.v1.get_meta_keywords(), u"This is the meta keywords of product 1")
        
        # Now we switch to active meta keywords.
        self.v1.active_meta_keywords = True
        self.v1.save()
        
        # Now we get the meta keywords of the variant
        self.assertEqual(self.v1.get_meta_keywords(), u"This is the meta keywords of variant 1")

    def test_get_meta_description(self):
        """
        """
        # Test product
        self.assertEqual(self.p1.get_meta_description(), u"This is the meta description of product 1")
        
        # Test variant. By default the meta description of a variant is 
        # inherited from parent product.
        self.assertEqual(self.v1.get_meta_description(), u"This is the meta description of product 1")
        
        # Now we switch to active meta description.
        self.v1.active_meta_description = True
        self.v1.save()
        
        # Now we get the meta description of the variant
        self.assertEqual(self.v1.get_meta_description(), u"This is the meta description of variant 1")
        
    def test_get_name(self):
        """
        """
        # Test product
        self.assertEqual(self.p1.get_name(), u"Product 1")
        
        # Test variant. By default the name of a variant is *not* inherited 
        self.assertEqual(self.v1.get_name(), u"Variant 1")
        
        # Now we switch to deactive name.
        self.v1.active_name = False
        self.v1.save()
        
        # Now we get the description of the parent product
        self.assertEqual(self.v1.get_name(), u"Product 1")

    def test_get_option(self):
        """
        """
        # Test variant 1 
        option = self.v1.get_option(property_id = self.color.id)
        self.assertEqual(option, self.red.id)

        option = self.v1.get_option(property_id = self.size.id)
        self.assertEqual(option, self.m.id)

        # Test variant 2
        option = self.v2.get_option(property_id = self.color.id)
        self.assertEqual(option, self.green.id)

        option = self.v2.get_option(property_id = self.size.id)
        self.assertEqual(option, self.l.id)
        
        # Pass a roperty id that doesn't exists
        option = self.v1.get_option(property_id = "dummy")
        self.assertEqual(option, None)

    def test_get_options(self):
        """
        """
        options = self.v1.get_options()
        self.assertEqual(options, [self.pvo_color_red, self.pvo_size_m])

        options = self.v2.get_options()
        self.assertEqual(options, [self.pvo_color_green, self.pvo_size_l])
        
        # TODO: Test position
        
    def test_has_option(self):
        """
        """
        # Variant 1 has color/red and size/m
        result = self.v1.has_option(self.color.id, self.red.id)
        self.assertEqual(result, True)

        result = self.v1.has_option(self.size.id, self.m.id)
        self.assertEqual(result, True)

        result = self.v1.has_option(self.color.id, self.green.id)
        self.assertEqual(result, False)

        result = self.v1.has_option(self.size.id, self.l.id)
        self.assertEqual(result, False)

        result = self.v1.has_option("foo", "bar")
        self.assertEqual(result, False)

        # Variant 2 has color/green and size/l
        result = self.v2.has_option(self.color.id, self.green.id)
        self.assertEqual(result, True)

        result = self.v2.has_option(self.size.id, self.l.id)
        self.assertEqual(result, True)

        result = self.v2.has_option(self.color.id, self.red.id)
        self.assertEqual(result, False)

        result = self.v2.has_option(self.size.id, self.m.id)
        self.assertEqual(result, False)

        result = self.v2.has_option("foo", "bar")
        self.assertEqual(result, False)
        
    def test_get_price(self):
        """
        """
        # Test product
        self.assertEqual(self.p1.get_price(), 1.0)
        
        # Test variant. By default the price of a variant is *not* inherited 
        self.assertEqual(self.v1.get_price(), 2.0)
        
        # Now we switch to deactive price.
        self.v1.active_price = False
        self.v1.save()
        
        # Now we get the price of the parent product
        self.assertEqual(self.v1.get_price(), 1.0)
        
    def test_get_price_gross(self):
        """Tests the gross price of a product and a variant. Takes active_price 
        of the variant into account.
        """
        # Test product
        self.assertEqual(self.p1.get_price_gross(), 1.0)
        
        # Test variant. By default the price_gross of a variant is *not* inherited 
        self.assertEqual(self.v1.get_price_gross(), 2.0)
        
        # Now we switch to deactive price.
        self.v1.active_price = False
        self.v1.save()
        
        # Now we get the price gross of the parent product
        self.assertEqual(self.v1.get_price_gross(), 1.0)
        
    def test_get_price_net(self):
        """Tests the net price of a product and a variant. Takes active_price of 
        the variant into account.
        """
        # Test product
        self.assertEqual("%.2f" % self.p1.get_price_net(), "0.84")
        
        # Test variant. By default the price_net of a variant is *not* inherited, 
        # but the tax is.
        self.assertEqual("%.2f" % self.v1.get_price_net(), "1.68")
        
        # Now we switch to deactive price.
        self.v1.active_price = False
        self.v1.save()
        
        # Now we get the price net of the parent product
        self.assertEqual("%.2f" % self.v1.get_price_net(), "0.84")

    def test_get_standard_price_1(self):
        """Test the price vs. standard price for a product.
        """
        # By default get_standard_price returns then normal price of the product
        standard_price = self.p1.get_standard_price()
        self.assertEqual(standard_price, 1.0)
        
        # Switch to for sale
        self.p1.for_sale = True
        self.p1.save()

        # If the product is for sale ``get_price`` returns the for sale price
        price = self.p1.get_price() 
        self.assertEqual(price, 0.5)

        # But ``get_standard_price`` returns still the normal price
        standard_price = self.p1.get_standard_price()
        self.assertEqual(standard_price, 1.0)

    def test_get_standard_price_2(self):
        """Test the price vs. standard price for a variant. Takes ``active_price`` 
        into account.
        """
        # By default get_standard_price returns then normal price of the variant
        standard_price = self.v1.get_standard_price()
        self.assertEqual(standard_price, 2.0)
        
        # Switch to for sale
        self.v1.for_sale = True
        self.v1.save()

        # If the product is for sale ``get_price`` returns the for sale price
        price = self.v1.get_price() 
        self.assertEqual(price, 1.5)

        # But ``get_standard_price`` returns still the normal price
        standard_price = self.v1.get_standard_price()
        self.assertEqual(standard_price, 2.0)

        # Switch to active price == False
        self.v1.active_price = False
        self.v1.save()

        # By default get_standard_price returns then normal price of the product
        standard_price = self.v1.get_standard_price()
        self.assertEqual(standard_price, 1.0)
        
        # Switch the **variant** to for sale
        self.v1.for_sale = True
        self.v1.save()
        
        # This hasn't any consequence as the price attributes are taken 
        # from the parent product, this is also true for the ``for_sale`` 
        # attibute
        price = self.v1.get_price()
        self.assertEqual(price, 1.0)

        standard_price = self.v1.get_standard_price()
        self.assertEqual(standard_price, 1.0)

        # Switch the **product** to for sale
        self.p1.for_sale = True
        self.p1.save()
        
        # The variant has the for_sale price of the parent product (due to 
        # ``active_price`` price is false)
        price = self.v1.get_price() 
        self.assertEqual(price, 0.5)
        
        # The variant has the standard price of the parent product (due to 
        # ``active_price`` price is false)
        standard_price = self.v1.get_standard_price()
        self.assertEqual(standard_price, 1.0)

    def test_get_sku(self):
        """
        """
        # Test product
        self.assertEqual(self.p1.get_sku(), u"SKU P1")
        
        # Test variant. By default the sku of a variant is *not* inherited 
        self.assertEqual(self.v1.get_sku(), "SKU V1")
        
        # Now we switch to deactive sku.
        self.v1.active_sku = False
        self.v1.save()
        
        # Now we get the sku of the parent product
        self.assertEqual(self.v1.get_sku(), "SKU P1")

    def test_get_tax_rate(self):
        """
        """
        tax_rate = self.p1.get_tax_rate()
        self.assertEqual(tax_rate, 19.0)
        
        # The variant has the same tax rate as the parent product
        tax_rate = self.v1.get_tax_rate()
        self.assertEqual(tax_rate, 19.0)

        # Product 2 doesn't have an assigned tax rate, hence it should be 0.0
        tax_rate = self.p2.get_tax_rate()
        self.assertEqual(tax_rate, 0.0)
        
    def test_get_tax(self):
        """
        """
        tax = self.p1.get_tax()
        self.assertEqual("%.2f" % tax, "0.16")

        # The variant has the same tax rate as the parent product
        self.v1.active_price = False
        tax = self.v1.get_tax()
        self.assertEqual("%.2f" % tax, "0.16")
        
        # If the variant has an active price the tax has to take care of this.
        self.v1.active_price = True
        tax = self.v1.get_tax()
        self.assertEqual("%.2f" % tax, "0.32")
        
        # Product 2 doesn't have a assigned tax rate, hence the tax should 0.0
        tax = self.p2.get_tax()
        self.assertEqual("%.2f" % tax, "0.00")
        
    def test_get_related_products(self):
        """
        """
        names = [p.name for p in self.p1.get_related_products()]
        self.assertEqual(names, ["Product 2", "Product 3"])
    
        names = [p.name for p in self.p2.get_related_products()]
        self.assertEqual(names, [])
    
        names = [p.name for p in self.p3.get_related_products()]
        self.assertEqual(names, [])
     
    def test_has_related_products(self):
        """
        """
        result = self.p1.has_related_products()
        self.assertEqual(result, True)
    
        result = self.p2.has_related_products()
        self.assertEqual(result, False)
        
        result = self.p3.has_related_products()
        self.assertEqual(result, False)
        
    def test_has_variants(self):
        """
        """
        result = self.p1.has_variants()
        self.assertEqual(result, True)
    
        result = self.p2.has_variants()
        self.assertEqual(result, False)
        
    def test_get_variants(self):
        """
        """
        variants = self.p1.get_variants()
    
        self.assertEqual(len(variants), 2)        
        self.failIf(self.v1 not in variants)
        self.failIf(self.v2 not in variants)
        
    def test_get_variant_has_variant(self):
        """Tests the order of passed options doesn't matter and the correct 
        bevaviour if no variant exists for given options.
        """
        # Try the first variant (v1 - m, red)
        options = [
            "%s|%s" % (self.size.id, self.m.id),
            "%s|%s" % (self.color.id, self.red.id),            
        ]
        
        result = self.p1.has_variant(options)
        self.failUnless(result)
        
        variant = self.p1.get_variant(options)
        self.assertEqual(variant.id, self.v1.id)
        
        # The order of passed options doesn't matter.
        options = [
            "%s|%s" % (self.color.id, self.red.id),                    
            "%s|%s" % (self.size.id, self.m.id),
        ]
        
        result = self.p1.has_variant(options)
        self.failUnless(result)
        
        variant = self.p1.get_variant(options)
        self.assertEqual(variant.id, self.v1.id)
        
        # Let's try the other variant (v2 - l, green)
        options = [
            "%s|%s" % (self.size.id, self.l.id),
            "%s|%s" % (self.color.id, self.green.id),            
        ]
        
        result = self.p1.has_variant(options)
        self.failUnless(result)
    
        variant = self.p1.get_variant(options)
        self.assertEqual(variant.id, self.v2.id)
        
        # The order of passed options doesn't matter.
        options = [
            "%s|%s" % (self.color.id, self.green.id),
            "%s|%s" % (self.size.id, self.l.id),
        ]
    
        result = self.p1.has_variant(options)
        self.failUnless(result)
        
        variant = self.p1.get_variant(options)
        self.assertEqual(variant.id, self.v2.id)
        
        # Try to get a variant which doesn't exist
        options = [
            "%s|%s" % (self.color.id, self.green.id),
            "%s|%s" % (self.size.id, "xl"),
        ]
    
        result = self.p1.has_variant(options)
        self.failIf(result)
        
        variant = self.p1.get_variant(options)
        self.failIf(variant is not None)
    
    def test_get_default_variant(self):
        """Tests the default default_variant (which is the first one) and 
        explicitly assigned variants
        """
        # If no default variant is set we get the first added variant
        default_variant = self.p1.get_default_variant()
        self.assertEqual(default_variant.id, self.v1.id)
        
        # Now we set the default variant to Variant 1
        self.p1.default_variant = self.v1
        default_variant = self.p1.get_default_variant()
        self.assertEqual(default_variant.id, self.v1.id)
    
        # Now we set the default variant to Variant 2
        self.p1.default_variant = self.v2
        default_variant = self.p1.get_default_variant()
        self.assertEqual(default_variant.id, self.v2.id)
    
        # Now we set the default variant to Variant 2
        default_variant = self.p2.get_default_variant()
        self.assertEqual(default_variant, None)
        
    def test_sub_type(self):
        """Tests the sub type of products.
        """
        self.assertEqual(self.p1.is_standard_product(), False)
        self.assertEqual(self.p1.is_product_with_variants(), True)
        self.assertEqual(self.p1.is_variant(), False)
    
        self.assertEqual(self.p2.is_standard_product(), True)
        self.assertEqual(self.p2.is_product_with_variants(), False)
        self.assertEqual(self.p2.is_variant(), False)
    
        self.assertEqual(self.v1.is_standard_product(), False)
        self.assertEqual(self.v1.is_product_with_variants(), False)
        self.assertEqual(self.v1.is_variant(), True)

class ProductAccessoriesTestCase(TestCase):
    """Tests ProductAccessories (surprise, surprise).
    """
    def setUp(self):
        """
        """
        self.p1 = Product.objects.create(name=u"Product 1", slug=u"product-1", price=1.0)
        self.p2 = Product.objects.create(name=u"Product 2", slug=u"product-2", price=2.0)
        self.p3 = Product.objects.create(name=u"Product 3", slug=u"product-3", price=3.0)
        
    def test_defaults(self):
        """Tests default values after creation.
        """
        pa = ProductAccessories.objects.create(product=self.p1, accessory=self.p2)
        self.assertEqual(pa.position, 999)
        self.assertEqual(pa.quantity, 1)
        
    def test_get_price(self):
        """Tests the calculation of the total price of a product accessory.
        """
        # Product 1 gets two accessories
        pa1 = ProductAccessories.objects.create(product=self.p1, accessory=self.p2, position=1, quantity=1)
        pa2 = ProductAccessories.objects.create(product=self.p1, accessory=self.p3, position=2, quantity=2)

        self.assertEqual(pa1.get_price(), 2.0)
        self.assertEqual(pa2.get_price(), 6.0)