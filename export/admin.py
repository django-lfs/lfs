# django imports
from django.contrib import admin

# lfs imports
from lfs.export.models import Export
from lfs.export.models import Script

admin.site.register(Export)
admin.site.register(Script)