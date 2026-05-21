#encoding:utf-8
from django.urls import reverse
from django.utils.text import slugify
from app.catalog.images import procesar_imagen_portada, procesar_imagen_logo
from datetime import datetime, date
from random import randint
from django.forms import model_to_dict
from django.db import models
from django.contrib.auth.forms import User
from .choices import MONEY
from meta.models import ModelMeta
from ventas import settings

class Tipo_company(models.Model):
    """Model definition for Categoria  ."""
    name = models.CharField('Categoria', max_length=50)
    description = models.CharField('Descripción',max_length=255, blank=True, null=True)
    icono = models.CharField('Icono de Bootstrap', default="bi bi-shop-window",max_length=50)
    is_new = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_mod = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for Categoria   ."""
        ordering = ['name']
        verbose_name = 'Tipo_company'
        verbose_name_plural = 'Tipo_companys'
    
    def __str__(self):
        """Unicode representation of Categoria ."""
        return self.name

    # Métodos para django-meta (SEO)
    def get_meta_title(self):
        return f"{self.name}"

    def get_meta_description(self):
        return (self.description or "")[:160]

    def get_meta_url(self):
        return f"/{self.id}/type"

    def num_vistos(self):
        num = randint(1500,5000)
        return num

class Ciudad(models.Model):
    """Model definition for Cuidad."""
    ciudad = models.CharField('Lugar/Ciudad', max_length=50)

    class Meta:
        """Meta definition for Cuidad."""

        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudads'

    def __str__(self):
        """Unicode representation of Cuidad."""
        return self.ciudad

    # Métodos para django-meta (SEO)
    def get_meta_title(self):
        return f"{self.ciudad}"
    
    def get_meta_description(self):
        return f"Explora empresas, productos y servicios disponibles en {self.ciudad.title()}, Bolivia."

    def get_meta_url(self):
        return f"/{self.id}/city"

class Plataforma(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre")
    description = models.CharField(max_length=150, verbose_name="Descripción")
    
    contracts_min = models.CharField(verbose_name="Tiempo de minimo", max_length=50)
    price_min = models.IntegerField(verbose_name="Precio")

    contracts_max = models.CharField(verbose_name="Tiempo de maximo", max_length=50)
    price_max = models.IntegerField(verbose_name="Precio")

    icono = models.CharField(max_length=100, verbose_name="Icono de Bootstrap", default="bi bi-clipboard2-check")
    qr_img = models.ImageField(upload_to='img_qr', null=True, blank=True, verbose_name='Img QR de pago', help_text="Imagen que tenga validacion de un año")

    cantidad = models.IntegerField(null=True, blank=True, verbose_name="Cantidad de registros permitidos")
    ilimitado = models.BooleanField(default=False, verbose_name="Es ilimitado")
    class Meta:
        """Meta definition for Cuidad."""

        verbose_name = 'Plataforma'
        verbose_name_plural = 'Plataformas'
    
    def __str__(self):
        """Unicode representation of Cuidad."""
        return self.name

class Company(models.Model, ModelMeta):
    name = models.CharField(max_length=50, verbose_name='Nombre/Razón social')
    description = models.TextField(verbose_name='Descripción de su catalogo (Opcional)', null=True, blank=True, help_text='Escriba una descripción sobre su negocio')
    ruc = models.CharField(max_length=15, blank=True, null=True, verbose_name='Número de NIT (Opcional)')
    #address = models.CharField(max_length=200, verbose_name='Dirección (Zona, Calle, #)')
    mobile = models.CharField(max_length=15, verbose_name='Celular (WhatsApp)')
    category = models.ForeignKey(Tipo_company, on_delete=models.CASCADE, verbose_name='Tipo de Negocio')
    cuidad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, verbose_name='Seleccione su Ciudad')
    #phone = models.CharField(max_length=9, verbose_name='Teléfono convencional')
    #email = models.CharField(max_length=50, verbose_name='Email')
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    website = models.CharField(max_length=250, verbose_name='Link a grupo de WhatsApp (Opcional)', blank=True, null=True, help_text="Tus clientes se uniran mediante este link")
    #iva = models.DecimalField(default=0.00, decimal_places=2, max_digits=9, verbose_name='IVA')
    moneda = models.CharField(max_length=50, choices=MONEY, default=MONEY[0][0], verbose_name='Seleccione su moneda')
    image = models.ImageField(null=True, blank=True, upload_to='company/portada/%Y/', verbose_name='Imagen de Portada (Opcional)')
    logo = models.ImageField(null=True, blank=True, upload_to='company/logo/%Y/', verbose_name='Logo (Opcional)')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    plan = models.ForeignKey(Plataforma, on_delete=models.CASCADE, verbose_name="Seleccione un plan")
    expiration_date = models.DateField(verbose_name='Fecha de expiracion (dd/mm/AAAA)')
    status = models.BooleanField(default=True, verbose_name="Estado")
    is_service = models.BooleanField(default=False, verbose_name='Marque esta opción, solo si su negocio es de tipo servicio.', help_text="Ej. restauranes o productos consumibles que dificultan el envío a lugares alejados")

    def save(self, *args, **kwargs):
        if self.image:# Si hay imagen nueva o editada
            procesar_imagen_portada(self, 'image')  # Procesar primero la imagen antes de guardar
        if self.logo:
            procesar_imagen_logo(self, 'logo')

        super().save(*args, **kwargs)  # Guardar ya procesada
        # si no existe dominio asociado, lo creamos
        # Crear dominio si no existe
        if not hasattr(self, "dominio"):
            base_slug = slugify(self.name)
            slug = base_slug
            contador = 1
            # Evitar duplicados
            while Dominio.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{contador}"
                contador += 1
            # Crear Dominio con slug único
            Dominio.objects.create(company=self, slug=slug)

    def __str__(self):
        return self.name

    # Métodos para django-meta (SEO)
    def get_meta_title(self):
        return f"{self.name}"

    def get_meta_description(self):
        return (self.description or "")[:160]

    def get_meta_image(self):
        if self.image:
            return f'{settings.MEDIA_URL}{self.image}'
        return f"{settings.STATIC_URL}img/default/empty.png"

    def get_meta_url(self):
        try:
            return f"/{self.dominio.slug}"
        except Exception:
            # fallback si no tiene dominio
            return f"/{self.id}/catalogo"
    
    def contarLikes(self):
        from app.catalog.models import Like
        suma_likes = Like.objects.filter(company_id=self.id).aggregate(like=models.Sum('like'))
        if suma_likes['like'] == None:
            suma_likes = {'like':0}
            return suma_likes
        else:
            return suma_likes

    def get_iva(self):
        return float(self.iva)

    def get_image(self):
        if self.image:
            return f'{settings.MEDIA_URL}{self.image}'
        return f'{settings.STATIC_URL}img/default/empty.png'
    
    @property
    def get_logo(self):
        if self.logo:
            return self.logo.url

        if self.image:
            return self.image.url
        return f'{settings.STATIC_URL}img/default_store.jpg'

    def toJSON(self):
        item = model_to_dict(self)
        item['id'] = int(self.id)
        item['name'] = self.name
        item['mobile'] = self.mobile
        item['description'] = self.description
        item['is_service'] = self.is_service
        item['moneda'] = self.moneda
        item['image'] = self.get_image()
        item['logo'] = self.get_logo()
        return item

    class Meta:
        verbose_name = 'Negocio'
        verbose_name_plural = 'Negocios'
        default_permissions = ()
        permissions = (
            ('view_company', 'Can view Empresa'),
        )

class Cupon(models.Model):
    codigo = models.CharField(max_length=255, verbose_name="Ingrese el Código del Cupon", help_text="Una o mas palabra separadas por coma Ej: 1234,tienda,negocio123")
    descuento = models.IntegerField(help_text="Ingrese el porcentaje del descuento %")
    estado = models.BooleanField(default=True, help_text="Indica que estara activo en todas las compras")
    company = models.OneToOneField(Company, on_delete=models.CASCADE)

    class Meta:
        """Meta definition for Bancos."""
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
    """Model definition for Bancos."""
    name = models.CharField(max_length=50, verbose_name='Nombre del Banco')
    destinatario = models.CharField(max_length=60, verbose_name='A Nombre de')
    cuenta = models.CharField(max_length=50, verbose_name='Nro. de cuenta')
    qr_img = models.ImageField(null=True, blank=True, upload_to='img_qr', verbose_name='Img QR de pago', help_text="Recomendación que sea valido de un año o mas")
    company = models.OneToOneField(Company, on_delete=models.CASCADE, verbose_name='Negocio')
    class Meta:
        """Meta definition for Bancos."""
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
        #item['company'] = self.category.toJSON()
        return item

class Sucursal(models.Model):
    company=models.OneToOneField(Company, on_delete=models.CASCADE, verbose_name='Negocio')
    address = models.TextField(max_length=200, verbose_name='Dirección de todas sus sucursales y Horario')
    latitud=models.CharField(max_length=50, verbose_name='Latitud')
    longitud=models.CharField(max_length=50, verbose_name='Longitud')
    date_joined = models.DateTimeField(auto_now_add=True)

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
    company = models.OneToOneField(Company, on_delete=models.CASCADE, verbose_name='Negocio')
    precio = models.IntegerField(verbose_name='Precio de envio a domicilio')
    precio_ciudad = models.IntegerField(verbose_name='Precio de envio a otra ciudad')
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company.name

    def toJSON(self):
        item = model_to_dict(self)
        item['company'] = self.company.name
        item['id'] = int(self.id)
        item['precio'] = self.precio
        item['precio_ciudad'] = self.precio_ciudad
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        return item

class Aviso(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, verbose_name='Negocio')
    Tiempo_entrega = models.CharField(verbose_name='Tiempo de Entrega', max_length=50, help_text="Ejemplo: En 24 Hrs.")
    envios = models.CharField(verbose_name='Lugar de envio', max_length=50, help_text="Ejemplo: Envios a todo el pais")
    pedidos = models.CharField(verbose_name='Pedidos', max_length=50, help_text="Ejemplo: Pedidos las 24 hrs.")
    pide_ahora = models.CharField(verbose_name='Metodo de Pedir', max_length=50, help_text="Ejemplo: Pide ahora y pague en casa")

    def __str__(self):
        return self.company.name

    def toJSON(self):
        item = model_to_dict(self)
        item['company'] = self.company.name
        item['Tiempo_entrega'] = self.Tiempo_entrega
        item['envios'] = self.envios
        item['pedidos'] = self.pedidos
        item['pide_ahora'] = self.pide_ahora
        return item


class Condicion(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, verbose_name='Negocio')
    regla = models.TextField(verbose_name='Terminos y condiciones', max_length=255, help_text="Escriba las reglas y condiciones para sus ventas")

    def __str__(self):
        return self.company.name

    def toJSON(self):
        item = model_to_dict(self)
        item['company'] = self.company.name
        item['regla'] = self.regla
        return item

class RRSS(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Negocio')
    icono = models.CharField(verbose_name='Icono', max_length=50)
    rrss = models.CharField(verbose_name='redes sociales', max_length=255)

    def __str__(self):
        return self.company.name

    def toJSON(self):
        item = model_to_dict(self)
        item['company'] = self.company.name
        item['rrss'] = self.rrss
        return item

class PixelMeta(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, verbose_name='Negocio')
    codigo = models.CharField(max_length=50, verbose_name='Pixel_id', null=True, blank=True, help_text='Copie pixel id de Meta')
    def __str__(self):
        return self.company.name

    def toJSON(self):
        item = model_to_dict(self)
        item['company'] = self.company.name
        item['codigo'] = self.codigo
        return item

class Suscripcion(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Negocio')
    email = models.EmailField(max_length=255)

    class Meta:
        unique_together = ('company', 'email')  # no puede repetirse para el email para la misca company
        verbose_name = "Suscripción"
        verbose_name_plural = "Suscripciones"

    def __str__(self):
        return self.company.name

    def toJSON(self):
        item = model_to_dict(self)
        item['company'] = self.company.name
        item['email'] = self.email
        return item

class Dominio(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='dominio')
    slug = models.SlugField(max_length=255, unique=True, verbose_name="El dominio por defecto es", help_text="Puede editarlo el dominio solo una vez (recomendado)")

    def save(self, *args, **kwargs):
        # Genera automáticamente el slug a partir del nombre de la empresa si no existe
        if not self.slug:
            self.slug = slugify(self.company.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self, request=None):
        """
        Devuelve la URL completa del dominio.
        Si se pasa request, construye URL dinámica.
        """
        if request:
            return request.build_absolute_uri(f'/{self.slug}/')
        else:
            # URL por defecto si no se pasa request
            return f'/{self.slug}/'

    def __str__(self):
        return f"{self.company.name} - {self.slug}"
