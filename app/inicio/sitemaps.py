from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from app.catalog.models import Company, Product

class IndexSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ['inicio']  # El nombre de tu vista en urls.py

    def location(self, item):
        return reverse(item)

class CompanySitemap(Sitemap):
    changefreq = "weekly"

    def items(self):
        return Company.objects.filter(status=True)

    def location(self, obj):
        try:
            return f"/{obj.dominio.slug}"
        except Exception:
            # fallback si no tiene dominio
            return f"/{obj.id}/catalogo"
        
    def lastmod(self, obj):
        # Usa el campo date_joined o si tienes un date_update mejor aún
        return obj.date_joined
    
    def priority(self, obj):
        # Más prioridad si tiene productos
        if obj.product_set.exists():
            return 1.0
        return 0.8

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Product.objects.filter(company__status=True)

    def location(self, obj):
        return f'/{obj.id}/{obj.company.id}/detail_product'