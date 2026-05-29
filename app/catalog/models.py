# encoding:utf-8
from datetime import datetime
from django.db import models
from django.forms import model_to_dict
from app.inicio.models import *
from ventas import settings
from app.catalog.choices import *

class Dashboard(models.Model):

    name = models.CharField(max_length=50,unique=True,verbose_name='Nombre del Sistema')

    author = models.CharField(
        max_length=120,
        default="jjavierl"
    )

    codigo = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Pixel Meta'
    )

    favicon = models.ImageField(
        upload_to='dashboard/favicon/',
        null=True,
        blank=True
    )
    navbar = models.CharField(max_length=50, choices=NAVBAR, default=NAVBAR[0][0], verbose_name='Navbar')

    color_texto = models.CharField(max_length=50, default='#000000', verbose_name='Color del texto')
    class Meta:
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboard'

    

    def __str__(self):
        return self.name
    
    def get_image(self):
        if self.image:
            return self.image.url
        return f'{settings.STATIC_URL}img/default/empty.png'
    
    @property
    def get_logo(self):
        if self.logo:
            return self.logo.url

        if self.image:
            return self.image.url

        return f'{settings.STATIC_URL}img/default_store.jpg'

    def toJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'author': self.author,
            'codigo': self.codigo,
            'favicon': self.get_image(),
            'navbar': self.navbar,
            'color_texto': self.color_texto
        }

class Video(models.Model):
    video = models.URLField(max_length=255, verbose_name='URL Video', help_text='Copie la url(link) del video')
    items = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name='Producto')

    class Meta:
        verbose_name = 'video'
        verbose_name_plural = 'videos'

    def __str__(self):
        return f'{self.video} ({self.items.name})'


class Orden(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Cliente')
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Sub Total')
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Descuento')
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Total a pagar')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora de registro')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Ordens'

    def __str__(self):
        return self.client.names

    def toJSON(self):
        item = model_to_dict(self)
        item['id'] = int(self.id)
        item['client'] = self.client.names
        item['sub_total'] = self.subtotal
        item['total'] = self.total
        return item


class Pedido(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cant = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    nota = models.TextField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'{self.product.name}, orden # {self.orden}'


class Like(models.Model):
    like = models.IntegerField(verbose_name='like')
    date_joined = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Cliente')
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, verbose_name='Orden')

    class Meta:
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'

    def __str__(self):
        return self.company.name



class Bank_dashboard(models.Model):
    """Model definition for Bancos."""
    name = models.CharField(max_length=50, verbose_name='Nombre del Banco')
    cuenta = models.CharField(max_length=50, verbose_name='Nro. de cuenta')
    qr_img = models.ImageField(null=True, blank=True, upload_to='img_qr', verbose_name='Img QR de pago', help_text="Imagen que tenga validacion de un año")
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, verbose_name='Negocio')
    class Meta:
        """Meta definition for Bancos."""

        verbose_name = 'Banco'
        verbose_name_plural = 'Bancos'

    def __str__(self):
        """Unicode representation of Bancos."""
        return self.name
    
class Cupon(models.Model):
    codigo = models.CharField(
        max_length=255,
        verbose_name='Ingrese el Código del Cupon',
        help_text='Una o mas palabra separadas por coma Ej: 1234,tienda,negocio123',
    )
    descuento = models.IntegerField(help_text='Ingrese el porcentaje del descuento %')
    estado = models.BooleanField(default=True, help_text='Indica que estara activo en todas las compras')

    class Meta:
        db_table = 'tiendas_cupon'
        verbose_name = 'cupon'
        verbose_name_plural = 'cupones'

    def __str__(self):
        return self.codigo

    def toJSON(self):
        item = model_to_dict(self)
        item['company'] = self.company.name
        item['codigo'] = self.codigo
        item['descuento'] = self.descuento
        item['estado'] = self.estado
        return item


class Banco(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nombre del Banco')
    destinatario = models.CharField(max_length=60, verbose_name='A Nombre de')
    cuenta = models.CharField(max_length=50, verbose_name='Nro. de cuenta')
    qr_img = models.ImageField(
        null=True,
        blank=True,
        upload_to='img_qr',
        verbose_name='Img QR de pago',
        help_text='Recomendación que sea valido de un año o mas',
    )

    class Meta:
        db_table = 'tiendas_banco'
        verbose_name = 'Banco'
        verbose_name_plural = 'Bancos'

    def __str__(self):
        return self.name

    def get_image(self):
        if self.qr_img:
            return f'{settings.MEDIA_URL}{self.qr_img}'
        return f'{settings.STATIC_URL}img/empty.png'

    def toJSON(self):
        item = model_to_dict(self)
        item['name'] = self.name
        item['destinatario'] = self.destinatario
        item['cuenta'] = self.cuenta
        item['qr_img'] = self.get_image()
        return item


class Sucursal(models.Model):
    address = models.TextField(max_length=200, verbose_name='Dirección de todas sus sucursales y Horario')
    latitud = models.CharField(max_length=50, verbose_name='Latitud')
    longitud = models.CharField(max_length=50, verbose_name='Longitud')
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tiendas_sucursal'

    def __str__(self):
        return self.company.name

    def toJSON(self):
        item = model_to_dict(self)
        item['company'] = self.company.name
        item['address'] = self.address
        item['latitud'] = self.latitud
        item['longitud'] = self.longitud
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        return item


class Precio_envio(models.Model):
    precio = models.IntegerField(verbose_name='Precio de envio a domicilio')
    precio_ciudad = models.IntegerField(verbose_name='Precio de envio a otra ciudad')
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tiendas_precio_envio'

    def __str__(self):
        return f"{self.precio} - {self.precio_ciudad}"

    def toJSON(self):
        item = model_to_dict(self)
        item['company'] = self.company.name
        item['id'] = int(self.id)
        item['precio'] = self.precio
        item['precio_ciudad'] = self.precio_ciudad
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        return item


class Aviso(models.Model):
    mensaje1 = models.CharField(
        verbose_name='Mensaje 1',
        max_length=50,
    )
    mensaje2 = models.CharField(
        verbose_name='Mensaje 2',
        max_length=50,
    )
    mensaje3 = models.CharField(
        verbose_name='Mensaje 3',
        max_length=50,
    )
    mensaje4 = models.CharField(
        verbose_name='Mensaje 4',
        max_length=50,
    )

    class Meta:
        db_table = 'tiendas_aviso'

    def toJSON(self):
        item = model_to_dict(self)
        item['mensaje1'] = self.mensaje1
        item['mensaje2'] = self.mensaje2
        item['mensaje3'] = self.mensaje3
        item['mensaje4'] = self.mensaje4
        return item


class Condicion(models.Model):
    regla = models.TextField(
        verbose_name='Requisitos para la compra a credito',
        max_length=255,
        help_text='Escriba los requisitos para la compra a credito, Ejemplo: Tener una antiguedad de 6 meses como cliente.',
    )

    class Meta:
        db_table = 'tiendas_condicion'

    def toJSON(self):
        item = model_to_dict(self)
        item['regla'] = self.regla
        return item


class RRSS(models.Model):
    icono = models.CharField(verbose_name='Icono', max_length=50)
    rrss = models.CharField(verbose_name='redes sociales', max_length=255)

    class Meta:
        db_table = 'tiendas_rrss'

    def __str__(self):
        return self.rrss

    def toJSON(self):
        item = model_to_dict(self)
        item['rrss'] = self.rrss
        return item


class PixelMeta(models.Model):
    codigo = models.CharField(
        max_length=50,
        verbose_name='Pixel_id',
        null=True,
        blank=True,
        help_text='Copie pixel id de Meta',
    )

    class Meta:
        db_table = 'tiendas_pixelmeta'

    def __str__(self):
        return self.company.name

    def toJSON(self):
        item = model_to_dict(self)
        item['codigo'] = self.codigo
        return item


class Suscripcion(models.Model):
    celular = models.CharField(max_length=10, verbose_name='WhatsApp')

    class Meta:
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'

    def __str__(self):
        return self.celular

    def toJSON(self):
        item = model_to_dict(self)
        item['celular'] = self.celular
        return item