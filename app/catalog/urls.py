from django.urls import path

from app.catalog.views import *


urlpatterns = [
    path('', CatalogView.as_view(), name='CatalogView'),
    path('optenerProducto/<int:id_producto>', optenerProducto, name='optenerProducto'),
    path('ver_carrito/', ver_carrito, name='ver_carrito'),
    path('vaciar_carrito/', vaciar_carrito, name='vaciar_carrito'),
    path('eliminarProducto/<int:id_producto>', eliminarProducto, name='eliminarProducto'),
]