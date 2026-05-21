"""
URL configuration for ventas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.urls import path, include
from django.conf.urls.static import static
from ventas import settings

from django.contrib.sitemaps.views import sitemap
from app.inicio.sitemaps import *
from app.inicio.views import robots_txt, password_reset_confirm_ajax

sitemaps = {
    'inicio': IndexSitemap,
    'companies': CompanySitemap,
    'products': ProductSitemap,
    'categorias': TipoCompanySitemap,
    'ciudades':CiudadSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.inicio.urls')),
    path('', include('app.catalog.urls')),
    path('', include('app.tiendas.urls')),
    path("robots.txt", robots_txt, name="robots_txt"),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('auth/', include('social_django.urls', namespace='social')),
    
    path(
        'reset_password/',
        auth_views.PasswordResetView.as_view(
            template_name="password_reset.html",
            success_url='/reset_password_send/'  # Redirige correctamente
        ),
        name='password_reset'
    ),
    path('reset_password_send/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', password_reset_confirm_ajax, name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
