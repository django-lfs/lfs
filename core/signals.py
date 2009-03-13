# django imports
import django.dispatch

# Catalog
cart_changed = django.dispatch.Signal()
category_changed = django.dispatch.Signal()
product_changed = django.dispatch.Signal()
lfs_sorting_changed = django.dispatch.Signal()

# Order
order_submitted = django.dispatch.Signal()

# Marketing
topseller_changed = django.dispatch.Signal()
