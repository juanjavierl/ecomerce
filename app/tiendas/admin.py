import random
from decouple import config
from django.shortcuts import render, redirect
from django.urls import path
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.contrib import admin, messages
from datetime import date, timedelta
# Register your models here.
from app.tiendas.models import *
from app.catalog.models import Product
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .forms import AdminEmailForm
admin.site.register([Banco,Ciudad,Tipo_company,Plataforma, Sucursal,Precio_envio, Aviso, Condicion, RRSS, PixelMeta, Dominio])

class companias_expirados(admin.SimpleListFilter):
    title = "Catálogos Expirados"
    parameter_name = "expirados"
    
    def lookups(self, request, model_admin):
        return (
            ('menos2', 'Expirados recientes (<2 meses)'),
            ('mas2', 'Expirados +2 meses'),
            ('vigentes', 'Vigentes'),
        )
    
    def queryset(self, request, queryset):
        limite = date.today() - timedelta(days=60)
        hoy = date.today()
        if self.value() == 'mas2':
            # Expirados hace más de 2 meses
            return queryset.filter(expiration_date__lt=limite)

        if self.value() == 'menos2':
            # Expirados dentro de los últimos 60 días
            return queryset.filter(expiration_date__lt=date.today(),expiration_date__gte=limite)
        if self.value() == 'vigentes':
            # Aún vigentes
            return queryset.filter(expiration_date__gte=hoy)
        
        return queryset

companias_expirados.short_description = 'Catalogos Expirados'

class CompanyResource(resources.ModelResource):

    class Meta:
        model = Company

@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
    resource_class = CompanyResource
    list_display = (
        'id',
        'name',
        'date_joined',
        'plan',
        'status',
        'expiration_date',
        'ruc',
        'mobile',
        'cuidad'
    )
    search_fields = ('name','ruc','id',)
    list_filter = ('plan', companias_expirados)
    
    actions = ['enviar_email_action']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'enviar-email/',
                self.admin_site.admin_view(self.enviar_email_view),
                name='enviar_email_companias',
            ),
        ]
        return custom_urls + urls

    def enviar_email_action(self, request, queryset):
        ids = ",".join(str(obj.id) for obj in queryset)
        return redirect(f"enviar-email/?ids={ids}")

    enviar_email_action.short_description = "📧 Enviar email personalizado"

    def enviar_email_view(self, request):
        ids = request.GET.get("ids", "")
        company_ids = [int(i) for i in ids.split(",") if i.isdigit()]
        companies = Company.objects.filter(id__in=company_ids)

        if request.method == "POST":
            form = AdminEmailForm(request.POST)
            if form.is_valid():
                subject = form.cleaned_data["subject"]
                message = form.cleaned_data["message"]

                for company in companies:
                    user_email = getattr(company.user, "email", None)
                    if not user_email:
                        continue  # Saltar si el usuario no tiene correo

                    from_email = config("EMAIL_HOST_USER")
                    to = [user_email]

                    html_content = render_to_string(
                        "email_admin/admin_message.html",
                        {"company": company, "message": message}
                    )
                    msg = EmailMultiAlternatives(subject, message, from_email, to)
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                self.message_user(
                    request,
                    f"✅ Emails enviados a {companies.count()} compañías.",
                    level=messages.SUCCESS,
                )
                return redirect("..")
        else:
            form = AdminEmailForm()

        return render(request, "email_admin/send_email_form.html", {
            "form": form,
            "companies": companies
        })

class SuscripResource(resources.ModelResource):
    class Meta:
        model = Suscripcion


@admin.register(Suscripcion)
class SuscripcionAdmin(ImportExportModelAdmin):
    resource_class = SuscripResource
    list_display = (
        'id',
        'company',
        'email',
    )
    search_fields = ('email',)
    list_filter = ('company',)

    actions = ["enviar_promociones"]

    def enviar_promociones(self, request, queryset):
        """
        Envía un email a cada suscriptor con hasta 3 productos 
        en promoción, nuevos o aleatorios de cada compañía suscrita.
        Incluye la URL absoluta a la compañía.
        """
        # Agrupamos suscripciones por email
        suscriptores = {}
        for sus in queryset:
            if sus.email not in suscriptores:
                suscriptores[sus.email] = []
            suscriptores[sus.email].append(sus.company)

        enviados = 0
        for email, companies in suscriptores.items():
            companies_data = []
            for company in companies:
                # buscamos primero promociones
                productos = Product.objects.filter(
                    company=company,
                    is_promotion=True
                )[:3]

                # si no hay en promoción, probamos con nuevos
                if not productos.exists():
                    productos = Product.objects.filter(
                        company=company,
                        is_new=True
                    )[:3]

                # si tampoco hay, elegimos aleatorios
                if not productos.exists():
                    product_ids = list(
                        Product.objects.filter(company=company).values_list("id", flat=True)
                    )
                    if product_ids:  # verificamos que haya productos
                        random_ids = random.sample(product_ids, min(3, len(product_ids)))
                        productos = Product.objects.filter(id__in=random_ids)

                if productos.exists():
                    # construimos URL absoluta de la compañía
                    company_url = request.build_absolute_uri(
                        f"/{company.id}/catalogo"
                    )
                    companies_data.append({
                        "company": company,
                        "productos": productos,
                        "url": company_url
                    })

            if not companies_data:
                continue  # nada que enviar para este suscriptor

            subject = "🎉 Mira las promociones y novedades"
            from_email = settings.EMAIL_HOST_USER
            to = [email]

            html_content = render_to_string(
                "email_admin/promociones.html",
                {
                    "companies_data": companies_data,
                    "request": request,  # para que el template pueda usar build_absolute_uri si es necesario
                }
            )

            msg = EmailMultiAlternatives(subject, "", from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            enviados += 1

        self.message_user(
            request,
            f"✅ Se enviaron correos a {enviados} suscriptores.",
            level=messages.SUCCESS,
        )

    enviar_promociones.short_description = "📩 Enviar promociones/novedades a suscriptores"
