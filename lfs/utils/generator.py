# python imports
import os
import sys

# django imports
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect

from lfs.catalog.models import Category
from lfs.catalog.models import Image
from lfs.catalog.models import Product
from lfs.core.models import Shop

from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption

from lfs.shipping.models import ShippingMethod
from lfs.criteria.models import CartPriceCriterion

def generate_shipping(request):
    """
    """
    ShippingMethod.objects.all().delete()
    sm1 = ShippingMethod.objects.create(name="Standard", active=True)
    sm2 = ShippingMethod.objects.create(name="Express", active=True)
    
    pc = CartPriceCriterion.objects.create()
    sm1.criteria_objects.create(criterion=pc)
    
    return HttpResponseRedirect("/shops")
    
def generate_categories(request):
    """
    """
    Category.objects.all().delete()
    
    for i in range(0, 10):        
        c = Category(name="Category %s" % i, slug="category-%s" % i)
        c.save()
        for j in range(0, 3):
            sc = Category(name="Category %s%s" % (i, j), slug="category-%s-%s" % (i, j), parent=c)
            sc.save()
            for k in range(0, 3):
                ssc = Category(name="Category %s%s%s" % (i, j, k), slug="category-%s-%s-%s" % (i, j, k), parent=sc)
                ssc.save()

    return HttpResponseRedirect("/shops")
    
def products(request):
    """
    """    
    amount = int(request.GET.get("amount", 20))
    
    Image.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    Shop.objects.all().delete()
    PropertyOption.objects.all().delete()
    Property.objects.all().delete()
    
    # Images
    path = os.path.join(sys.path[0], "lfs/utils/data")
    fh = open(os.path.join(path, "image1.jpg"))
    cf_1 = ContentFile(fh.read())
    fh = open(os.path.join(path, "image2.jpg"))
    cf_2 = ContentFile(fh.read())
    fh = open(os.path.join(path, "image3.jpg"))
    cf_3 = ContentFile(fh.read())
    
    image_1 = Image(title="Image 1")    
    image_1.image.save("Laminat01.jpg", cf_1)
    image_1.save()

    image_2 = Image(title="Image 2")
    image_2.image.save("Laminat02.jpg", cf_2)
    image_2.save()

    image_3 = Image(title="Image 3")
    image_3.image.save("Laminat03.jpg", cf_3)
    image_3.save()

    # Properties
    property = Property(name="Color")
    property.save()

    property_option= PropertyOption(name = "Yellow", property = property, price = 1.0)
    property_option.save()

    property_option = PropertyOption(name = "Red", property = property, price = 2.0)
    property_option.save()

    property = Property(name="Size")
    property.save()

    property_option = PropertyOption(name = "L", property = property, price = 11.0)
    property_option.save()

    property_option = PropertyOption(name = "M", property = property, price = 12.0)
    property_option.save()
    
    # Create shop
    shop = Shop(name="Test", shop_owner="Test")
    shop.save()

    # Create categories
    category_1 = Category(name="Clothes", slug="clothes")
    category_1.save()
    
    category_2 = Category(name="Women", slug="women", parent=category_1)
    category_2.save()

    category_3 = Category(name="Pants", slug="pants-woman", parent=category_2)
    category_3.save()

    category_4 = Category(name="Dresses", slug="dresses", parent=category_2)
    category_4.save()

    category_5 = Category(name="Men", slug="men", parent=category_1)
    category_5.save()

    category_6 = Category(name="Pants", slug="pants-men", parent=category_5)
    category_6.save()

    category_7 = Category(name="Pullover", slug="pullover", parent=category_5)
    category_7.save()
    
    shop.categories = [category_1, category_2, category_3, category_4, category_5, category_6, category_7]
    shop.save()
    
    # Create products
    for i in range(1, amount):
        p = Product(name="1-%s" % i, slug="1-%s" % i, price=i)
        p.save()

        if i == 1:
            p.images.add(image_1)
            p.images.add(image_2)
            p.images.add(image_3)
            p.save()            
        else:
            img = Image(title="Image 1", image="images/Laminat01.jpg")
            img.save()
            p.images.add(img)
            p.save()
        
        category_3.products.add(p)
        category_3.save()
        
        print "1-%s created" % i
        

    for i in range(1, amount):
        p = Product(name="2-%s" % i, slug="2-%s" % i, price=i*10)
        p.save()

        img = Image(title="Image 1", image="images/Laminat02.jpg")
        img.save()
        p.images.add(img)
        p.save()

        category_4.products.add(p)
        category_4.save()

        print "2-%s created" % i
    
    for i in range(1, amount):
        p = Product(name="3-%s" % i, slug="3-%s" % i, price=i*100)
        p.save()

        img = Image(title="Image 1", image="images/Laminat03.jpg")
        img.save()
        p.images.add(img)
        p.save()

        category_6.products.add(p)
        category_6.save()

        print "3-%s created" % i

    for i in range(1, amount):
        p = Product(name="4-%s" % i, slug="4-%s" % i, price=i*100)
        p.save()

        img = Image(title="Image 1", image="images/Laminat03.jpg")
        img.save()
        p.images.add(img)
        p.save()

        category_7.products.add(p)
        category_7.save()

        print "4-%s created" % i
    
    product = Product.objects.get(slug="1-1")

    return HttpResponseRedirect("/shops")