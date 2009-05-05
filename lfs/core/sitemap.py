from django.contrib.sitemaps import Sitemap
from lfs.catalog.models import Product

class ProductSitemap(Sitemap):
    """Google's XML sitemap for products.
    """
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.creation_date