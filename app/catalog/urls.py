from django.urls import path

from app.catalog.views import *


urlpatterns = [
    path('', CatalogView.as_view(), name='CatalogView'),
    path('optenerProducto/<int:id_producto>', optenerProducto, name='optenerProducto'),
    path('ver_carrito/', ver_carrito, name='ver_carrito'),
    path('vaciar_carrito/', vaciar_carrito, name='vaciar_carrito'),
    path('eliminarProducto/<int:id_producto>', eliminarProducto, name='eliminarProducto'),
    path('shear_product/',shear_product, name='eliminarProducto'),
    path('mostrar_por_categoria/<int:id_categoria>', mostrar_por_categoria, name='mostrar_por_categoria'),
    path('confirmar_pedido/',confirmar_pedido,name="confirmar_pedido"),

    path('login/', login_user, name="login"),
    path('salir/', salir, name='salir'),

    path('pdf/', pdf_view, name='pdf'),
]