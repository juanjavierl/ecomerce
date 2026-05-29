# encoding:utf-8
from datetime import datetime
from random import randint

from app.catalog.choices import *
from django.contrib.auth import get_user_model
from django.db import models
from django.forms import model_to_dict
from meta.models import ModelMeta
from app.catalog.images import procesar_imagen
from ventas import settings

User = get_user_model()
# Create your models here.

class Company(models.Model, ModelMeta):

    name = models.CharField(
        max_length=50,
        verbose_name='Nombre/Razón social'
    )
    nit = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Descripción del negocio'
    )

    mobile = models.CharField(
        max_length=15,
        verbose_name='WhatsApp'
    )

    email = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    address = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    ciudad = models.CharField(
        max_length=100
    )

    moneda = models.CharField(
        max_length=50,
        choices=MONEY,
        default=MONEY[0][0]
    )

    image = models.ImageField(
        upload_to='company/portada/',
        null=True,
        blank=True
    )

    logo = models.ImageField(
        upload_to='company/logo/',
        null=True,
        blank=True
    )

    button = models.CharField(max_length=150, verbose_name='Boton de Accion', help_text='Ingrese el texto del boton de accion')

    status = models.BooleanField(
        default=True
    )

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresa'


    def get_meta_title(self):
        return f"{self.name}"

    def get_meta_description(self):
        return (self.description or "")[:160]
    
    def get_meta_image(self):
        if self.image:
            return f'{settings.MEDIA_URL}{self.image}'
        return f"{settings.STATIC_URL}img/default/empty.png"
    
    def get_mata_url(self):
        return f"/{self.id}/"

    def toJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'nit': self.nit,
            'description': self.description,
            'mobile': self.mobile,
            'email': self.email,
            'address': self.address,
            'ciudad': self.ciudad,
            'moneda': self.moneda,
            'image': self.get_meta_image(),
            'button': self.button
        }

    def __str__(self):
        return self.name
    

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Nombre')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        item['name'] = self.name
        return item


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    code = models.CharField(max_length=20, blank=True, null=True, verbose_name='Código')
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Categoría')
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Precio de Venta')
    price_before = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.00,
        verbose_name='Precio Antes',
    )
    image = models.ImageField(
        upload_to='product/',
        default='default.png',
        blank=True,
        null=True,
        verbose_name='Imagen',
    )
    stock = models.IntegerField(default=1)
    salida = models.IntegerField(default=0, blank=True, null=True)
    is_promotion = models.CharField(
        max_length=50,
        choices=IS_PROMOTION,
        default=IS_PROMOTION[0][0],
        verbose_name='¿Elija una opcion?',
    )
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    date_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def save(self, *args, **kwargs):
        if self.image:
            procesar_imagen(self, 'image')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name()

    def get_meta_title(self):
        return f'{self.name} - {self.company.name}'

    def get_meta_description(self):
        if self.description:
            return self.description
        return f'Compra {self.name} en la categoría {self.category.name}.'

    def get_meta_image(self):
        return self.get_image()

    def get_meta_url(self):
        return f'/detail_product/{self.id}/'

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
        item['price_before'] = float(self.price_before)
        item['image'] = self.get_image()
        return item

    def porcentage(self):
        total = (self.price_before - self.price) / self.price * 100
        return int(total)

    def num_aleatorio(self):
        return randint(1, 11)

    def stock_actual(self):
        return int(self.stock) - int(abs(self.salida))


class Imagen(models.Model):
    img = models.ImageField(
        upload_to='img_products',
        default='default.png',
        verbose_name='Imagen',
        help_text='Puede registrar hasta 2 imagenes como maximo',
    )
    items = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='producto')

    class Meta:
        verbose_name = 'Imagen'
        verbose_name_plural = 'Imagenes'

    def save(self, *args, **kwargs):
        if self.img:
            procesar_imagen(self, 'img')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.img} ({self.items.name})'
    

class Client(models.Model):
    names = models.CharField(max_length=150, verbose_name='Nombre completo')
    dni = models.IntegerField(null=True, blank=True, verbose_name='Nro. Carnet/Nit (Opcional)')
    mobile = models.CharField(max_length=15, verbose_name='Celular (WhatsApp)')
    email = models.EmailField(max_length=100, unique=True, verbose_name='Correo Electrónico')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    address = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='Dirección o referencia exacta*',
        help_text='Ingrese:Zona,Calle,Nro',
    )

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.names}'

    def toJSON(self):
        item = model_to_dict(self)
        item['names'] = self.get_full_name()
        item['gender'] = {'id': self.gender, 'name': self.get_gender_display()}
        item['dni'] = self.dni
        item['id'] = int(self.id)
        item['mobile'] = self.mobile
        return item