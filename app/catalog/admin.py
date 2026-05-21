from django.contrib import admin

# Register your models here.
from app.catalog.models import *

from import_export import resources
from import_export.admin import ImportExportModelAdmin

admin.site.register([Category, Pedido, Like, Imagen, Video])

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'names',
        'dni',
        'mobile',
        'address',
        'date_joined',
        'email',
    )
    search_fields = ('names','dni',)

class ProductResource(resources.ModelResource):

    class Meta:
        model = Product

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = (
        'name',
        'code',
        'category',
        'company',
        'price',
        'stock',
        'date_joined',
    )
    search_fields = ('name','code',)
    list_filter = ('company',)

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = (
        'company',
        'client',
        'subtotal',
        'dscto',
        'total',
        'date_joined',
    )
    search_fields = ('date_joined','id',)