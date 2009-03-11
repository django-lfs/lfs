# django imports
from django.contrib import admin

# lfs imports
from lfs.criteria.models import CriteriaObjects
from lfs.criteria.models import CartPriceCriterion
from lfs.criteria.models import WeightCriterion
from lfs.criteria.models import CountryCriterion

class CartPriceCriterionAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(CartPriceCriterion, CartPriceCriterionAdmin)

class CountryCriterionAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(CountryCriterion, CountryCriterionAdmin)

class WeightCriterionAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(WeightCriterion, WeightCriterionAdmin)

class CriteriaObjectsAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(CriteriaObjects, CriteriaObjectsAdmin)

