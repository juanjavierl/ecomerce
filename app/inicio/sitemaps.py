from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from app.catalog.models import Company, Product


class IndexSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return ['CatalogView']

    def location(self, item):
        return reverse(item)


class CompanySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        company = Company.objects.filter(status=True).first()
        return [company] if company else []

    def location(self, obj):
        return '/'

    def lastmod(self, obj):
        return obj.date_joined


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return f'/detail_product/{obj.id}/'
