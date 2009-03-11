# django imports
from django.contrib import admin

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.models import Image
from lfs.catalog.models import Product
from lfs.catalog.models import ProductAccessories
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption
from lfs.catalog.models import StaticBlock
from lfs.catalog.models import DeliveryTime

class CategoryAdmin(admin.ModelAdmin):
    """
    """
    repopulated_fields = {"slug": ("name",)}
admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}
admin.site.register(Product, ProductAdmin)

class ImageAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(Image, ImageAdmin)

class ProductAccessoriesAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(ProductAccessories, ProductAccessoriesAdmin)

class PropertyAdmin(admin.ModelAdmin):
    """
    """    
admin.site.register(Property, PropertyAdmin)

class PropertyOptionAdmin(admin.ModelAdmin):
    """
    """    
admin.site.register(PropertyOption, PropertyOptionAdmin)

class StaticBlockAdmin(admin.ModelAdmin):
    """
    """    
admin.site.register(StaticBlock, StaticBlockAdmin)

class DeliveryTimeAdmin(admin.ModelAdmin):
    """
    """    
admin.site.register(DeliveryTime, DeliveryTimeAdmin)