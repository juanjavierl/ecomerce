#import las views de tiendas para mantener compatibilidad con imports legacy
from datetime import datetime, timedelta
import json
import threading

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, User
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db.models import F, ExpressionWrapper, IntegerField, Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template, render_to_string
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

from app.catalog.company_helpers import get_company
from app.catalog.forms import AffiliateRegisterForm, formProducto
from app.catalog.models import *
from app.catalog.views.catalog import *
from app.inicio.views import get_Dashboard
from app.inicio.forms import *
from ventas import settings

def newCategory(request):
    if request.method == 'POST':
        form = formCategory(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.save()
            return JsonResponse({'category_name':cat.name, 'category_id':cat.id})
        else:
            return JsonResponse({'error':'La Categoria ya Existe o Datos Invalidos.'})
    form = formCategory()
    return render(request, 'catalog/newCategory.html',{'form':form})

def updateProduct(request, id_product):
    product = Product.objects.get(id=id_product)
    if request.method=='POST':
        form=formUpdateProducto(request.POST, request.FILES,instance=product)
        if form.is_valid():
            form.save()
            return JsonResponse({'redirect_url': '/'})
    else:
        form=formUpdateProducto(instance=product)
        return render(request, 'catalog/updateProduct.html',{'form':form,'product':product})

def deleteProduct(request, id_product):
    product = get_object_or_404(Product, id=int(id_product))
    if request.method == 'POST':
        product.delete()
        return JsonResponse({'redirect_url': '/'})
    return render(request,'catalog/deleteProduct.html',{'product':product})

def updateStock(request, id_product):
    product = get_object_or_404(Product, id=int(id_product))
    if request.method=='POST':
        if int(request.POST['incremento']) > 0 and int(request.POST['decremento']) == 0:
            cant = int(request.POST['incremento'])

            Product.objects.filter(id=id_product).update(stock = int(product.stock) + cant)
            return JsonResponse({'success':'Bien Stock Actualizado'})
        elif int(request.POST['incremento']) == 0 and int(request.POST['decremento']) > 0:
            cant = int(request.POST['decremento'])
            Product.objects.filter(id=id_product).update(salida =  cant + int(abs(product.salida)))

            return JsonResponse({'success':'Bien Stock Actualizado'})
        else:
            return JsonResponse({'error':'Los datos estan en 0, ingrese una cantidad.'})
    else:
        return render(request, 'catalog/updateStock.html',{'p':product})

def imgs_products(request, id_producto):
    product = Product.objects.get(id=id_producto)
    if request.method=='POST':
        print(request.FILES)
        form=FormImgProducto(request.POST, request.FILES)
        if form.is_valid():
            imgsProducto = form.save(commit=False)
            imgsProducto.items_id = (int(id_producto))
            if Imagen.objects.filter(items_id = int(id_producto)).count() >= 5:
                return JsonResponse({'error':'Ya tiene registrado sus imagenes'})
            else:
                imgsProducto.save()
                return JsonResponse({'success':'Registro exitoso'})
        else:
            return JsonResponse({'error': form.errors})
    else:
        form=FormImgProducto()
    return render(request, 'catalog/imgs_products.html',{'form':form,'product':product})

def remode_imgs_products(request, id_producto):
    imagenes = Imagen.objects.filter(items_id = int(id_producto))
    return render(request, 'catalog/remode_imgs_products.html',{'imagenes':imagenes})

def deleteImgProduct(request, id_img):
    image = get_object_or_404(Imagen, id=int(id_img))
    image.delete()
    return JsonResponse({'success':'Se Elimino la Imagen'})

def getPrecioEnvio(request):
    datos = {}
    opcion = request.GET.get('opcion', 'domicilio')
    datos['total'] = calcular_pago(request)

    banco = getBanco()
    datos['qr'] = banco.toJSON() if banco else False

    if opcion == "domicilio":
        precio = determinarPrecioEnvio()
        datos['precio_envio'] = precio
        datos['total_pagar'] = int(calcular_pago(request)) + int(precio or 0)
    elif opcion == "ciudad":
        precio = determinarPrecioEnvioCiudad()
        datos['precio_envio'] = precio
        datos['total_pagar'] = int(calcular_pago(request)) + int(precio or 0)
    else:
        datos['precio_envio'] = 0
        datos['total_pagar'] = calcular_pago(request)

    datos['importe'] = calcular_pago(request)
    return JsonResponse({'datos': datos})

def form_sheart_product(request):
    return render(request, 'catalog/form_sheart_product.html', {'company': get_company()})

def login_user(request):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return redirect('/')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=request.POST['username'],
                password=request.POST['password'],
            )
            if user is not None:
                login(request, user)
                company = Company.objects.first()
                return JsonResponse({'redirect_url': '/'})
            return JsonResponse({'error': 'Contactese con el administrador para resolver el problema gracias.'})
        return JsonResponse({'error': 'Datos incorrectos intente nuevamente gracias.'})

    return render(request, 'company/form_login.html', {'form': AuthenticationForm()})


def salir(request):
    logout(request)
    return redirect('/')


def validar_form(request):
    if request.method == 'POST':
        formulario = formCompany(data=request.POST)
        if formulario.is_valid():
            return JsonResponse({'formulario': True})
        return JsonResponse({'error': formulario.errors})
    return JsonResponse({'error': 'Método no permitido'})



def registrar_afiliado(request):
    if request.method == 'POST':
        form = AffiliateRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            afiliados_group, _ = Group.objects.get_or_create(name='Afiliados')
            user.groups.add(afiliados_group)
            print('celular:', form.cleaned_data['celular'].strip())
            AffiliateProfile.objects.create(
                user=user,
                celular=form.cleaned_data['celular']
            )
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return JsonResponse({
                'success': 'Registro exitoso. Ya formas parte del programa de afiliados.',
                'redirect_url': '/',
            })
        return JsonResponse({'error': form.errors}, status=400)

    return render(request, 'afiliados/form_afiliado.html', {'form': AffiliateRegisterForm()})


def redirigir_a_catalogo(request, slug):
    return redirect('/')


@login_required(login_url='/')
def add_huvicacion(request):
    ubicacion = Sucursal.objects.first()
    if request.method == 'POST':
        form_huvicacion = FormHuvicacion(request.POST, instance=ubicacion)
        if form_huvicacion.is_valid():
            form_huvicacion.save()
            return JsonResponse({'success': 'Registro exitoso.'})
        return JsonResponse({'error': form_huvicacion.errors})
    else:
        form_huvicacion = FormHuvicacion(instance=ubicacion)
        return render(request, 'company/configuraciones/add_mapa.html', {'form_huvicacion': form_huvicacion, 'ubicacion': ubicacion})
    
    """ if request.method == 'POST':
        ubicacion, created = Sucursal.objects.get_or_create()
        ubicacion.address = request.POST['address']
        ubicacion.latitud = request.POST['latitud']
        ubicacion.longitud = request.POST['longitud']
        ubicacion.save()
        return JsonResponse({'success': 'Registro exitoso.'})
    return JsonResponse({'error': 'Método no permitido'}) """


def info_address_company(request):
    address = get_address()
    return render(request, 'company/notificaciones/info_address_company.html', {'address': address})


def del_address_comp(request, id_address):
    address = get_object_or_404(Sucursal, id=int(id_address))
    if request.method == 'POST':
        address.delete()
        return JsonResponse({'success': 'Se Borro el registro.'})
    return render(request, 'company/notificaciones/del_addres_company.html', {'address': address})

@login_required(login_url='/')
def dashboard_afiliado(request):
    comisiones = AffiliateCommission.objects.filter(affiliate=request.user).order_by('-id')
    pendientes = comisiones.filter(status='pending')
    aprobadas = comisiones.filter(status='approved')
    pagadas = comisiones.filter(status='paid')
    total_ganado = (pagadas.aggregate(total=Sum('commission_amount'))['total']or 0)
    print('Total ganado y sumado:', total_ganado)
    context = {
        'productos_compartidos': comisiones.count(),
        'pendientes': pendientes.count(),
        'aprobadas': aprobadas.count(),
        'pagadas': pagadas.count(),
        'total_ganado': total_ganado,
        'comisiones': comisiones,
        'company': Company.objects.first(),
        'categorias': categorys_from_productos(Product.objects.filter(stock__gt=0).order_by('-id')),
    }
    return render(
        request,
        'afiliados/dashboard_afiliado.html',
        context
    )

def info_afiliado(request, id_afiliado):
    user_afiliado = get_object_or_404(User, id=int(id_afiliado), groups__name='Afiliados')
    comisiones = AffiliateCommission.objects.filter(affiliate=id_afiliado).order_by('-id')
    pendientes = comisiones.filter(status='pending')
    aprobadas = comisiones.filter(status='approved')
    pagadas = comisiones.filter(status='paid')
    total_ganado = (pagadas.aggregate(total=Sum('commission_amount'))['total']or 0)
    context = {
        'productos_compartidos': comisiones.count(),
        'pendientes': pendientes.count(),
        'aprobadas': aprobadas.count(),
        'pagadas': pagadas.count(),
        'total_ganado': total_ganado,
        'comisiones': comisiones,
        'user_afiliado': user_afiliado,
    }
    return render(
        request,
        'afiliados/info_afiliado.html',
        context
    )

@login_required(login_url='/')
def configuraciones_company(request):
    if request.user.groups.filter(name='Afiliados').exists():
        return dashboard_afiliado(request)
    else:
        company = get_company(request.user)
        pedidos = Orden.objects.values('client_id').order_by('-id').distinct()
        productos = Product.objects.filter(stock__gt=0).order_by('-id')
        dic = {
            'reglas': Condicion.objects.all(),
            #'precio': get_precio_envios(),
            'avisos': Aviso.objects.all()[:1],
            'banco': Banco.objects.all()[:1],
            'ordens': list(pedidos),
            'clientes': Client.objects.all().order_by('-id'),
            'categorias': categorys_from_productos(productos),
            'company': company,
            'total_compra': sum(item['cantidad'] for item in request.session.get('compra', [])),
            'address': get_address(),
            'redes': RRSS.objects.all(),
            'list_afiliados': User.objects.filter(groups__name='Afiliados').order_by('-id'),

            'form_huvicacion': FormHuvicacion(instance=Sucursal.objects.first()),
            'form_ban': FormBanco(instance=Banco.objects.first()),
            #'form_precio': PrecioForm(instance=Precio_envio.objects.first()),
            'form_avisos': Form_avisos(instance=Aviso.objects.first()),
            'form_regla': Form_condiciones(),
            'form_red_social': formRedSocial(),
        }
        return render(request, 'company/configuraciones_company.html', dic)


def get_precio_envios():
    return Precio_envio.objects.first() or False


@login_required(login_url='/')
def precio_envio(request):
    if request.method == 'POST':
        try:
            preci = Precio_envio.objects.first()
            if not preci:
                preci = Precio_envio.objects.create(
                    precio=request.POST['precio'],
                    precio_ciudad=request.POST['precio_ciudad']
                )
            else:
                preci.precio = request.POST['precio']
                preci.precio_ciudad = request.POST['precio_ciudad']
                preci.save()
            return JsonResponse({
                'success': 'Registro Exitoso.',
                'precio': preci.precio,
                'precio_ciudad': preci.precio_ciudad,
                'id_precio': preci.id,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return JsonResponse({'error': 'Método no permitido'})


@login_required(login_url='/')
def buscar_orden(request):
    if request.method == 'POST':
        cod = int(request.POST['codigo_orden'])
        try:
            orden = Orden.objects.get(id=cod)
            pedidos = Pedido.objects.filter(orden_id=orden.id)
            precio_envio_val = int(orden.total) - int(orden.subtotal)
        except Orden.DoesNotExist:
            orden, pedidos, precio_envio_val = None, None, None
        return render(
            request,
            'company/reportes/buscar_orden.html',
            {'orden': orden, 'pedidos': pedidos, 'precio_envio': precio_envio_val},
        )
    return HttpResponse(status=405)


@login_required(login_url='/')
def reportByRange(request):
    if request.method == 'POST':
        inicio = datetime.strptime(request.POST['startDate'], '%d-%m-%Y')
        final = datetime.strptime(request.POST['endDate'], '%d-%m-%Y')
        ordenes = Orden.objects.filter(
            date_joined__range=(
                datetime.strftime(inicio, '%Y-%m-%d'),
                datetime.strftime(final, '%Y-%m-%d'),
            )
        )
        return render(request, 'company/reportes/reportByRangeOrden.html', {'ordenes': ordenes})
    return HttpResponse(status=405)


@login_required(login_url='/')
def inventarioProductos(request):
    criterio = request.POST.get('criterio', 'todos')
    productos = Product.objects.select_related('category').annotate(
        stock_actual=ExpressionWrapper(F('stock') - F('salida'), output_field=IntegerField())
    )
    if criterio == 'con_stock':
        productos = productos.filter(stock_actual__gt=0)
    elif criterio == 'agotados':
        productos = productos.filter(stock_actual__lte=0)

    return render(
        request,
        'company/reportes/inventarioProductos.html',
        {
            'criterio': criterio,
            'productos': productos.order_by('category__name', '-id'),
        },
    )


@login_required(login_url='/')
def reporte_form(request, criterio):
    return render(
        request,
        'company/reportes/reporte_form.html',
        {'form': formProducto(), 'criterio': criterio},
    )


@login_required(login_url='/')
def reporte_inventario(request, criterio):
    if request.method == 'GET':
        seleccionados = [key for key, value in request.GET.items() if value == 'on']
        por_defecto = ['image', 'name', 'stock_actual']
        for attr in por_defecto:
            if attr not in seleccionados:
                seleccionados.append(attr)
        seleccionados.sort(key=lambda x: (x not in por_defecto, x))

        productos = Product.objects.select_related('category').annotate(
            stock_actual=ExpressionWrapper(F('stock') - F('salida'), output_field=IntegerField())
        )
        if criterio == 'con_stock':
            productos = productos.filter(stock_actual__gt=0)
        elif criterio == 'agotados':
            productos = productos.filter(stock_actual__lte=0)

        html = render_to_string(
            'company/reportes/reporte_inventario_pdf.html',
            {
                'productos': productos.order_by('category__name', '-id'),
                'seleccionados': seleccionados,
            },
        )
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename=reporte_inventario.pdf'
        HTML(string=html).write_pdf(response, font_config=FontConfiguration())
        return response
    return HttpResponse(status=405)


@login_required(login_url='/')
def add_avisos(request):
    if request.method == 'POST':
        aviso = Aviso.objects.first()
        form = Form_avisos(request.POST, instance=aviso)
        if form.is_valid():
            aviso = form.save()
            return JsonResponse({'success': 'Registro Exitoso.', 'avisos': aviso.toJSON()})
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': 'Metodo no permitido.'}, status=405)


def get_opciones(request):
    avisos = Aviso.objects.all()
    return render(request, 'company/notificaciones/get_opciones.html', {'avisos': avisos})


def del_precio(request, id_precio):
    precio = get_object_or_404(Precio_envio, id=int(id_precio))
    if request.method == 'POST':
        precio.delete()
        return JsonResponse({'success': 'Se Borro el registro correctamente. '})
    return render(request, 'company/notificaciones/del_precio.html', {'precio': precio})


@login_required(login_url='/')
def banco_envio(request):
    if request.method == 'POST':
        try:
            banco = Banco.objects.first()
            form_ban = FormBanco(request.POST,request.FILES,instance=banco)
            if form_ban.is_valid():

                formulario = form_ban.save(
                    commit=False
                )
                formulario.save()
                return JsonResponse({'success': 'Registro Exitoso.'})
            return JsonResponse({'error': form_ban.errors})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return JsonResponse({'error': 'Método no permitido'})


def infor_banco(request):
    banco = Banco.objects.all()[:1]
    return render(request, 'company/notificaciones/infor_banco.html', {'banco': banco})


def del_infor_banco_by_company(request, id_banco):
    banco = get_object_or_404(Banco, id=int(id_banco))
    if request.method == 'POST':
        banco.delete()
        return JsonResponse({'success': 'Se Borro el registro. '})
    return render(request, 'company/notificaciones/del_infor_banco_by_company.html', {'banco': banco})


def eliminar_opciones(request, id_aviso):
    aviso = get_object_or_404(Aviso, id=int(id_aviso))
    if request.method == 'POST':
        aviso.delete()
        return JsonResponse({'success': 'Se Borro el registro correctamente. '})
    return render(request, 'company/notificaciones/eliminar_opciones.html', {'aviso': aviso})


def print_orden(request, id_orden):
    tipo = request.GET.get('tipo', 'ticket')
    orden = get_object_or_404(
        Orden.objects.select_related('client'),
        id=id_orden,
    )
    pedidos = Pedido.objects.filter(orden=orden)
    precio_envio_val = orden.total - orden.subtotal
    context = {
        'orden': orden,
        'company': get_company(),
        'pedidos': pedidos,
        'precio_envio': precio_envio_val,
        'sucursal': get_address(),
    }
    template = 'company/reportes/report_order_pdf.html' if tipo == 'factura' else 'company/reportes/ticket_pdf.html'
    html = render_to_string(template, context, request=request)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{tipo}_orden_{orden.id}.pdf"'
    HTML(string=html).write_pdf(response, font_config=FontConfiguration())
    return response


def productosDeCatalogo(request):
    productos = Product.objects.filter(stock__gt=0).order_by('-id')
    page = request.GET.get('page', 1)
    try:
        paginator = Paginator(productos, 10)
        return paginator.page(page)
    except Exception:
        raise Http404


def like_company(request, id_orden, id_cliente):
    company = get_company()
    if request.method == 'POST':
        lik = Like()
        lik.like = int(request.POST['like'])
        lik.client_id = int(id_cliente)
        lik.orden_id = int(id_orden)
        lik.save()
        return JsonResponse({'success': 'Muchas gracias por su preserencia', 'ruta:': '/'})

    productos = productosDeCatalogo(request)
    base = {
        'categorias': categorys_from_productos(productos),
        'total_compra': sum(item['cantidad'] for item in request.session.get('compra', [])),
        't_pago': calcular_pago(request),
        'company': company,
        'aviso': optener_avisos_by_company(),
        'id_orden': id_orden,
        'id_cliente': id_cliente,
        'address': get_address(),
        'ruta:': '/',
    }
    if Like.objects.filter(orden_id=id_orden, client_id=id_cliente).exists():
        base['like'] = 'Muchas gracias por su preferencia'
    else:
        base['productos'] = productos
    return render(request, 'company/notificaciones/like_company.html', base)


@login_required(login_url='/')
def add_condiciones(request):
    if request.method == 'POST':
        form = Form_condiciones(request.POST)
        if form.is_valid():
            condicion = form.save()
            return JsonResponse({'success': 'Registro Exitoso.'})
        return JsonResponse({'error': form.errors}, status=400)


def get_condiciones(request):
    reglas = Condicion.objects.all()
    return render(request, 'company/notificaciones/get_condiciones.html', {'reglas': reglas})


def delete_regla(request, id_regla):
    regla = get_object_or_404(Condicion, id=int(id_regla))
    if request.method == 'POST':
        regla.delete()
        return JsonResponse({'success': 'Se Borro el registro. '})
    return render(request, 'company/notificaciones/delete_reglas.html', {'regla': regla})


def create_mail_suscripcion(user_mail, subject, template_name, context):
    template = get_template(template_name)
    content = template.render(context)
    message = EmailMultiAlternatives(
        subject=subject,
        body='',
        from_email=settings.EMAIL_HOST_USER,
        to=[user_mail],
    )
    message.attach_alternative(content, 'text/html')
    return message


def send_suscripcion_mail(email_user, url_tienda, company):
    mail = create_mail_suscripcion(
        email_user,
        'Bienvenido a ' + company.name.title(),
        'company/notificaciones/sucripcion_user_email.html',
        {'email_user': email_user, 'url_tienda': url_tienda, 'company': company},
    )
    mail.send(fail_silently=False)


""" def suscribirse(request):
    company = get_company()
    url_tienda = f'https://{request.get_host()}/'
    if request.method == 'POST':
        try:
            Suscripcion.objects.create(email=request.POST['email'])
            thread = threading.Thread(
                target=send_suscripcion_mail,
                args=(request.POST['email'].strip(), url_tienda, company),
            )
            thread.start()
            return JsonResponse({
                'success': '¡Gracias por suscribirte! Revisa tu correo(spam), te enviamos un código de cupón para tu compra.',
            })
        except Exception:
            return JsonResponse({'error': 'El email ya está suscrito.'})
    return JsonResponse({'error': 'Método no permitido'}) """

def suscribirse(request):
    print("suscribirse")
    if request.method == 'POST':
        celular = request.POST.get('celular')
        if not celular:
            return JsonResponse({'error': 'Ingrese un número.'})

        existe = Suscripcion.objects.filter(
            celular=celular
        ).exists()

        if existe:
            return JsonResponse({
                'error': 'El número ya existe.'
            })

        Suscripcion.objects.create(
            celular=celular
        )

        return JsonResponse({
            'success': 'Muchas gracias por suscribirte! Pronto te enviaremos un mensaje con todas las ofertas y novedades.'
        })

    return JsonResponse({
        'error': 'Método no permitido.'
    })


@login_required(login_url='/')
def estadoCompany(request):
    company = get_company(request.user)
    initial_url = request.build_absolute_uri('/')
    return render(
        request,
        'company/notificaciones/estadoCompany.html',
        {'company': company, 'initial_url': initial_url},
    )


@login_required(login_url='/')
def autorizar_orden(request, id_orden):
    orden = get_object_or_404(Orden, id=id_orden)
    if orden.status:
        return render(request, 'company/notificaciones/orden_autorizada.html', {'orden': orden})

    if request.method == 'POST':
        orden.status = True
        orden.save()
        pedidos = Pedido.objects.filter(orden=orden).select_related('product')
        for pedido in pedidos:
            producto = pedido.product
            Product.objects.filter(id=producto.id).update(
                salida=F('salida') + pedido.cant
            )
        AffiliateCommission.objects.filter(orden=orden, status='pending').update(status='approved')
        messages.success(request, 'La orden fue autorizada y el stock de productos actualizado.')
        return render(request, 'company/notificaciones/orden_autorizada.html', {'orden': orden})
    return render(request, 'company/notificaciones/autorizar_orden.html', {'orden': orden})
