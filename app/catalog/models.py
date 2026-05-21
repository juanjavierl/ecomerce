#encoding:utf-8
import os
from .images import procesar_imagen
from random import randint
from datetime import datetime
from django.db.models import Sum, FloatField
from django.db.models.functions import Coalesce
from django.forms import model_to_dict

from ventas import settings
from app.catalog.choices import GENDER

from django.db import models
from app.tiendas.models import *

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Nombre')
    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        item['name'] = self.name
        return item

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    code = models.CharField(max_length=20, blank=True,null=True, verbose_name='Código')
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Categoría')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Compania')
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Precio de Venta')
    #pvp = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Precio de Venta')
    price_before = models.DecimalField(max_digits=9,decimal_places=2,null=True, blank=True,default=0.00, verbose_name='Precio Antes')
    image = models.ImageField(upload_to='product/%Y', default="default.png", blank=True, null=True, verbose_name='Imagen')
    is_service = models.BooleanField(default=False, verbose_name='¿Es un servicio?')
    #with_tax = models.BooleanField(default=False, verbose_name='¿Se cobra impuesto?')
    stock = models.IntegerField(default=1)
    salida = models.IntegerField(default=0 ,blank=True,null=True)
    is_new = models.BooleanField(default=False, verbose_name='¿Es novedad?', help_text='marque solo si corresponde')
    is_promotion = models.BooleanField(default=False, verbose_name='¿Esta en promocion?',help_text='marque solo si corresponde')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    date_update = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.image:# Si hay imagen nueva o editada
            procesar_imagen(self, 'image')  # Procesar primero la imagen antes de guardar
        super().save(*args, **kwargs)  # Guardar ya procesada

    def __str__(self):
        return self.get_full_name()
    
    def get_meta_title(self):
        return f"{self.name} - {self.company.name}"

    def get_meta_description(self):
        if self.description:
            return self.description
        return f"Compra {self.name} en {self.company.name}, en la categoría {self.category.name}."

    def get_meta_image(self):
        return self.get_image()

    def get_meta_url(self):
        return f'/{self.id}/{self.company.id}/detail_product'

    def get_full_name(self):
        return f'{self.name} ({self.code}) ({self.category.name})'

    def get_short_name(self):
        return f'{self.name} ({self.category.name})'

    def get_image(self):
        if self.image:
            return f'{settings.MEDIA_URL}{self.image}'
        return f'{settings.STATIC_URL}img/default/empty.png'

    def toJSON(self):
        item = model_to_dict(self)
        item['full_name'] = self.get_full_name()
        item['short_name'] = self.get_short_name()
        item['category'] = self.category.toJSON()
        item['price'] = float(self.price)
        #item['pvp'] = float(self.pvp)
        item['price_before'] = float(self.price_before)
        item['image'] = self.get_image()
        return item

    def porcentage(self):
        total = (self.price_before - self.price)/self.price * 100
        return int(total)

    def num_aleatorio(self):
        num = randint(1,11)
        return num
    
    def stock_actual(self):
        en_stock = int(self.stock) - int(abs(self.salida))
        return en_stock

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

class Imagen(models.Model):
    img = models.ImageField(upload_to='img_products', default="default.png", verbose_name='Imagen', help_text="Puede registrar hasta 2 imagenes como maximo")
    items = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='producto')
    
    def save(self, *args, **kwargs):
        if self.img:# Si hay imagen nueva o editada
            procesar_imagen(self, 'img')  # Procesar primero la imagen antes de guardar
        super().save(*args, **kwargs)  # Guardar ya procesada

    def __str__(self):
        return f'{self.img} ({self.items.name})'
    
    class Meta:
        verbose_name = 'Imagen'
        verbose_name_plural = 'Imagenes'

class Video(models.Model):
    video = models.URLField(max_length=255, verbose_name='URL Video', help_text="Copie la url(link) del video")
    items = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name='Producto')
    
    def __str__(self):
        return f'{self.img} ({self.items.name})'
    
    class Meta:
        verbose_name = 'video'
        verbose_name_plural = 'videos'

class Client(models.Model):
    names = models.CharField(max_length=150, verbose_name='Nombre completo')
    dni = models.IntegerField(null=True, blank=True, verbose_name='Nro. Carnet/Nit (Opcional)')
    gender = models.CharField(max_length=50, choices=GENDER, default=GENDER[0][0], verbose_name='Genero')
    mobile = models.CharField(max_length=15, verbose_name='Celular (WhatsApp)')
    email = models.EmailField(max_length=100, unique=True, verbose_name='Correo Electrónico')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name='Dirección o referencia exacta*', help_text="Ingrese:Zona,Calle,Nro")

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.names}'

    def birthdate_format(self):
        return self.birthdate.strftime('%Y-%m-%d')

    def toJSON(self):
        item = model_to_dict(self)
        item['names'] = self.get_full_name()
        item['gender'] = {'id': self.gender, 'name': self.get_gender_display()}
        item['dni'] = self.dni
        item['id'] = int(self.id)
        item['mobile'] = self.mobile
        return item

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

class Orden(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Compañia')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Cliente')
    #employee = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Empleado')
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00,verbose_name='Sub Total')
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Descuento')
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Total a pagar')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora de registro')#Fecha de modificacion
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')#Fecha de registro
    status = models.BooleanField(default=False)
    # TODO: Define fields here

    class Meta:
        """Meta definition for Orden."""

        verbose_name = 'Orden'
        verbose_name_plural = 'Ordens'

    def __str__(self):
        return self.client.names

    def toJSON(self):
        item = model_to_dict(self)
        item['id'] = int(self.id)
        item['company'] = self.company.name
        item['client'] = self.client.names
        item['sub_total'] = self.subtotal
        item['total'] = self.total
        return item

class Pedido(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cant = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    nota = models.TextField(max_length=255, null=True, blank=True)

    class Meta:
        """Meta definition for Pedido."""

        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        """Unicode representation of Pedido."""
        return "%s, orden # %s"%(self.product.name, self.orden)


class Like(models.Model):
    like = models.IntegerField(verbose_name='like')
    date_joined = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Negocio')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Cliente')
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, verbose_name='Orden')

    class Meta:
        """Meta definition for Bancos."""
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'

    def __str__(self):
        return self.company.name