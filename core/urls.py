from django.conf.urls.defaults import *

# Shop
urlpatterns = patterns('lfs.core.views',
    url(r'^$', "shop_view", name="lfs_shop_view"),
)

# Catalog
urlpatterns += patterns('lfs.catalog.views',
    url(r'^kategorie-(?P<slug>[-\w]*)$', "category_view"),
    url(r'^get-categories-nodes$', "get_category_nodes"),    
    url(r'^kategorie-(?P<slug>[-\w]*)/(?P<start>\d*)$', "category_view", name="lfs_category"),
    url(r'^product/(?P<slug>[-\w]*)$', "product_view", name="lfs_product"),
    url(r'^product-form-dispatcher', "product_form_dispatcher", name="lfs_product_dispatcher"),
    url(r'^set-sorting', "set_sorting", name="lfs_catalog_set_sorting"),
    url(r'^set-product-filter/(?P<category_slug>[-\w]+)/(?P<property_id>\d+)/(?P<value>.+)', "set_filter", name="lfs_set_product_filter"),
    url(r'^set-price-filter/(?P<category_slug>[-\w]+)/$', "set_price_filter", name="lfs_set_price_filter"),
    url(r'^reset-price-filter/(?P<category_slug>[-\w]+)/$', "reset_price_filter", name="lfs_reset_price_filter"),
    url(r'^reset-product-filter/(?P<category_slug>[-\w]+)/(?P<property_id>\d+)', "reset_filter", name="lfs_reset_product_filter"),
    url(r'^reset-all-product-filter/(?P<category_slug>[-\w]+)', "reset_all_filter", name="lfs_reset_all_product_filter"),
)

# Cart
urlpatterns += patterns('lfs.cart.views',
    url(r'^add-to-cart$', "add_to_cart"),
    url(r'^add-accessory-to-cart/(?P<product_id>\d*)/(?P<quantity>.*)$', "add_accessory_to_cart", name="lfs_add_accessory_to_cart"),
    url(r'^added-to-cart$', "added_to_cart"),
    url(r'^delete-cart-item/(?P<cart_item_id>\d*)$', "delete_cart_item", name="lfs_delete_cart_item"),
    url(r'^refresh-cart$', "refresh_cart"),
    url(r'^cart$', "cart"),
)

# Manage
urlpatterns += patterns('',
    (r'^manage/', include('lfs.manage.urls')),
)

# Page
urlpatterns += patterns('lfs.page.views',
    url(r'^page/(?P<slug>[-\w]*)$', "page_view", name="lfs_page_view"),
)

# Search
urlpatterns += patterns('lfs.search.views',
    url(r'^search', "search", name="lfs_search"),
    url(r'^livesearch', "livesearch"),
)

# Checkout
urlpatterns += patterns('lfs.checkout.views',
    url(r'^checkout', "checkout", name="lfs_checkout"),
    url(r'^thank-you', "thank_you",name="lfs_thank_you"),
    url(r'^changed-checkout/$', "changed_checkout"),
    url(r'^changed-country/$', "changed_country"),
)

# utils
urlpatterns += patterns('lfs.utils.generator',
    (r'^generate-products$', "products"),
    (r'^generate-categories$', "generate_categories"),
    (r'^generate-shipping$', "generate_shipping"),
)