# encoding:utf-8
from datetime import datetime
from django.conf import settings as django_settings
from django.db import models
from django.forms import model_to_dict
from app.inicio.models import *
from ventas import settings
from app.catalog.choices import *
from django.db.models import Sum

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
    navbar = models.CharField(max_length=50, verbose_name='Color del Navbar', default='#000')

    color_texto = models.CharField(max_length=50, default='#fff', verbose_name='Color del texto')
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
    affiliate = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='affiliate_orders',
        limit_choices_to={'groups__name': 'Afiliados'},
        verbose_name='Afiliado',
    )
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
    
    @property
    def total_affiliate_commission(self):
        return (
            self.affiliate_commissions.aggregate(
                total=Sum('commission_amount')
            )['total'] or 0
        )

    def toJSON(self):
        item = model_to_dict(self)
        item['id'] = int(self.id)
        item['client'] = self.client.names
        item['affiliate'] = self.affiliate_id
        item['affiliate_username'] = self.affiliate.username if self.affiliate else None
        item['sub_total'] = self.subtotal
        item['total'] = self.total
        return item


class Pedido(models.Model):
    orden = models.ForeignKey(
        Orden,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='pedidos',
        verbose_name='Orden',
    )
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
        orden_id = self.orden_id if self.orden_id else 'Sin orden'
        return f'{self.product.name}, orden # {orden_id}'

class AffiliateCommission(models.Model):
    affiliate = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='affiliate_commissions',
        limit_choices_to={'groups__name': 'Afiliados'},
        verbose_name='Afiliado',
    )
    orden = models.ForeignKey(
        Orden,
        on_delete=models.CASCADE,
        related_name='affiliate_commissions',
        verbose_name='Orden',
    )
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name='affiliate_commission',
        verbose_name='Pedido',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='affiliate_commissions',
        verbose_name='Producto',
    )
    quantity = models.IntegerField(default=0, verbose_name='Cantidad')
    unit_price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Precio unitario')
    product_total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Total producto')
    commission_ganacia = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='Ganancia afiliado')
    commission_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Total ganacia')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora de registro')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')

    class Meta:
        verbose_name = 'Comisión de afiliado'
        verbose_name_plural = 'Comisiones de afiliados'

    def __str__(self):
        return f'{self.affiliate} - orden # {self.orden_id} - {self.commission_amount}'

class Like(models.Model):
    like = models.IntegerField(verbose_name='like')
    date_joined = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Cliente')
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, verbose_name='Orden')

    class Meta:
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'

    def __str__(self):
        company = Company.objects.first()
        return company.name if company else str(self.like)


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
        company = Company.objects.first()
        return company.name if company else self.address

    def toJSON(self):
        item = model_to_dict(self)
        company = Company.objects.first()
        item['company'] = company.name if company else ''
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
        company = Company.objects.first()
        item['company'] = company.name if company else ''
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
    pregunta = models.CharField(
        verbose_name='Pregunta frecuente',
        max_length=255,
    )
    regla = models.TextField(
        verbose_name='Respuesta a la pregunta frecuente',
        max_length=255,
        help_text='Escriba la respuesta a la pregunta frecuente.',
    )

    class Meta:
        db_table = 'tiendas_condicion'

    def toJSON(self):
        item = model_to_dict(self)
        item['pregunta'] = self.pregunta
        item['regla'] = self.regla
        return item


class RRSS(models.Model):
    rrss = models.CharField(verbose_name='Red Social', unique=True, max_length=50, choices=RRSS_CHOICES, default=RRSS_CHOICES[0][0], help_text='Seleccione la red social')
    enlace = models.URLField(verbose_name='Enlace', max_length=255, help_text='Copie el enlace de su red social')

    class Meta:
        db_table = 'tienda_rrss'

    def __str__(self):
        return self.rrss

    def toJSON(self):
        item = model_to_dict(self)
        item['rrss'] = self.rrss
        item['enlace'] = self.enlace
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
        company = Company.objects.first()
        return company.name if company else self.codigo

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


class AffiliateProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='affiliate_profile')
    celular = models.CharField(max_length=20, verbose_name='Celular')

    def __str__(self):
        return self.user.get_full_name() or self.user.username