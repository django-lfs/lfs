from django.conf.urls.defaults import *
from lfs.core.sitemap import ProductSitemap

handler500 = 'lfs.core.views.server_error'

urlpatterns = patterns('lfs.core.views',
    url(r'^$', "shop_view", name="lfs_shop_view"),
    url(r'^robots\.txt/$',  "robots", name="lfs_robots"),
)

# Sitemaps
urlpatterns += patterns("django.contrib.sitemaps.views",
    url(r'^sitemap.xml$', 'sitemap', {'sitemaps': {"products": ProductSitemap}})
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

# Catalog
urlpatterns += patterns('lfs.catalog.views',
    url(r'^category-(?P<slug>[-\w]*)$', "category_view", name="lfs_category"),
    url(r'^category-(?P<slug>[-\w]*)/(?P<start>\d*)$', "category_view", name="lfs_category"),
    url(r'^get-categories-nodes$', "get_category_nodes"),    
    url(r'^product/(?P<slug>[-\w]*)$', "product_view", name="lfs_product"),
    url(r'^product-form-dispatcher', "product_form_dispatcher", name="lfs_product_dispatcher"),
    url(r'^set-sorting', "set_sorting", name="lfs_catalog_set_sorting"),
    url(r'^set-product-filter/(?P<category_slug>[-\w]+)/(?P<property_id>\d+)/(?P<min>.+)/(?P<max>.+)', "set_filter", name="lfs_set_product_filter"),    
    url(r'^set-product-filter/(?P<category_slug>[-\w]+)/(?P<property_id>\d+)/(?P<value>.+)', "set_filter", name="lfs_set_product_filter"),
    url(r'^set-price-filter/(?P<category_slug>[-\w]+)/$', "set_price_filter", name="lfs_set_price_filter"),
    url(r'^reset-price-filter/(?P<category_slug>[-\w]+)/$', "reset_price_filter", name="lfs_reset_price_filter"),
    url(r'^reset-product-filter/(?P<category_slug>[-\w]+)/(?P<property_id>\d+)', "reset_filter", name="lfs_reset_product_filter"),
    url(r'^reset-all-product-filter/(?P<category_slug>[-\w]+)', "reset_all_filter", name="lfs_reset_all_product_filter"),
)

# Checkout
urlpatterns += patterns('lfs.checkout.views',
    url(r'^checkout-dispatcher', "checkout_dispatcher", name="lfs_checkout_dispatcher"),
    url(r'^checkout-login', "login", name="lfs_checkout_login"),
    url(r'^checkout', "one_page_checkout", name="lfs_checkout"),
    url(r'^thank-you', "thank_you",name="lfs_thank_you"),
    url(r'^changed-checkout/$', "changed_checkout"),
    url(r'^changed-country/$', "changed_country"),
)

# Customer
urlpatterns += patterns('lfs.customer.views',
    url(r'^login/$',  "login", name="lfs_login"),
    url(r'^logout/$', "logout", name="lfs_logout"),    
    url(r'^my-account', "account", name="lfs_my_account"),
    url(r'^my-addresses', "addresses", name="lfs_my_addresses"),
    url(r'^my-email', "email", name="lfs_my_email"),
    url(r'^my-orders', "orders", name="lfs_my_orders"),
    url(r'^my-order/(?P<id>\d+)', "order", name="lfs_my_order"),
    url(r'^my-password', "password", name="lfs_my_password"),
)

# Page
urlpatterns += patterns('lfs.page.views',
    url(r'^page/(?P<slug>[-\w]*)$', "page_view", name="lfs_page_view"),
    url(r'^pages/$', "pages_view", name="lfs_pages"),
    url(r'^popup/(?P<slug>[-\w]*)$', "popup_view", name="lfs_popup_view"),    
)

# Password reset
urlpatterns += patterns('django.contrib.auth.views',
     url(r'^password-reset/$', "password_reset", name="lfs_password_reset"),
     url(r'^password-reset-done/$', "password_reset_done"),
     url(r'^password-reset-confirm/(?P<uidb36>[-\w]*)/(?P<token>[-\w]*)$', "password_reset_confirm"),
     url(r'^password-reset-complete/$', "password_reset_complete"),     
)

# Search
urlpatterns += patterns('lfs.search.views',
    url(r'^search', "search", name="lfs_search"),
    url(r'^livesearch', "livesearch"),
)

# Utils
urlpatterns += patterns('lfs.utils.generator',
    (r'^generate-products$', "products"),
    (r'^generate-categories$', "generate_categories"),
    (r'^generate-shipping$', "generate_shipping"),
)

# 3rd party
urlpatterns += patterns('',
    (r'^utils', include('lfs.utils.urls')),
)

urlpatterns += patterns('',
    (r'^tagging/', include('lfs.tagging.urls')),
)