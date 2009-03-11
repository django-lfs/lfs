# django imports
from django.contrib import admin

# lfs imports
from lfs.core.models import Country
from lfs.core.models import Shop

class ShopAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(Shop, ShopAdmin)

class CountryAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(Country, CountryAdmin)