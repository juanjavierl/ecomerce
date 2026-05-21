from django.urls import path

from app.catalog import views


urlpatterns = [
    path('<int:id_company>/catalogo', views.CatalogView, name='CatalogView'),
    path('<int:id_producto>/<int:id_company>/detail_product', views.optenerProducto, name='detail_product'),
    path('<int:id_company>/ver_carrito/', views.ver_carrito, name='ver_carrito'),
    path('<int:id_company>/show_productos_carrito/', views.show_productos_carrito, name='show_productos'),
    path('vaciar_carrito/', views.vaciar_carrito, name='vaciar_carrito'),
    path('eliminarProducto/<int:id_producto>', views.eliminarProducto, name='eliminarProducto'),
    path('actualizarCantidad/', views.actualizarCantidad, name='actualizarCantidad'),
    path('<int:id_company>/shear_product/',views.shear_product, name='shear_product'),
    path('<int:id_company>/<int:id_categoria>/mostrar_por_categoria', views.mostrar_por_categoria, name='mostrar_por_categoria'),
    path('<int:id_company>/confirmar_compra/', views.confirmar_compra, name='confirmar_compra'),
    path('<int:id_company>/<int:id_producto>/confirmar_cita/', views.confirmarCita, name='confirmarCita'),
    path('<int:id_company>/new_producto/', views.newProducto, name='new_producto'),
    path('new_category/', views.newCategory, name='new_category'),

    path('<int:id_product>/updateProduct/', views.updateProduct, name='updateProduct'),
    path('<int:id_product>/deleteProduct/', views.deleteProduct, name='deleteProduct'),
    path('<int:id_product>/updateStock/', views.updateStock, name='updateStock'),
    path('<int:id_producto>/imgs_products/', views.imgs_products, name='imgs_products'),
    path('<int:id_producto>/remode_imgs_products/', views.remode_imgs_products, name='remode_imgs_products'),
    path('<int:id_img>/deleteImgProduct/', views.deleteImgProduct, name='deleteImgProduct'),
    path('<int:id_company>/getPrecioEnvio/', views.getPrecioEnvio, name='get_precios'),
    path('form_sheart_product/', views.form_sheart_product, name='form_sheart_product'),
]