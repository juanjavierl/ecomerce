
from django.shortcuts import render, get_object_or_404,HttpResponse,redirect
from django.contrib.auth.forms import User, UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, request,HttpResponse
from django.template.loader import render_to_string, get_template
from django.core.paginator import Paginator
from django.db.models import Count, Sum, F
from django.contrib import messages
from ventas import settings
from django.core.mail import EmailMultiAlternatives
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from datetime import datetime, date, timedelta
import os
import json
import threading
import ast
from app.tiendas.models import *
from app.tiendas.forms import *
from app.catalog.forms import formProducto
from app.catalog.models import Product, Orden, Pedido, Like
from app.inicio.views import get_Dashboard
from app.catalog.views import *
from django.db.models import F, ExpressionWrapper, IntegerField
# Create your views here.
def getTypes(request, id_type):
    if request.user.is_authenticated:
        companys = Company.objects.filter(user_id = int(request.user.id))
    else:
        companys = Company.objects.filter(category=int(id_type), status=True)
    count_productos = {}
    for c in companys:
        count_productos[c.name] = Product.objects.filter(company_id = int(c.id)).count()
   
    request.session['compra'] = []#inicializa el carrito vacio nuevamente
    dic = {
        'category':getType(id_type),
        'companys':companys,
        'dashboard':get_Dashboard(),
        'count_productos':count_productos,
        'ciudades':Ciudad.objects.all().order_by('-id'),
        'type_company':Tipo_company.objects.all().order_by('-id'),
        'count_comp':contar_companys()
    }
    return render(request, 'card_companys.html', dic)

def getCiudades(request, id_ciudad):
    if request.user.is_authenticated:
        companys = Company.objects.filter(user_id = int(request.user.id))
    else:
        companys = Company.objects.filter(cuidad=int(id_ciudad), status=True)
    count_productos = {}
    for c in companys:
        count_productos[c.name] = Product.objects.filter(company_id = int(c.id)).count()

    request.session['compra'] = []#inicializa el carrito vacio nuevamente
    dic = {
        'ciudad':getCity(id_ciudad),
        'companys':companys,
        'dashboard':get_Dashboard(),
        'count_productos':count_productos,
        'ciudades':Ciudad.objects.all().order_by('-id'),
        'type_company':Tipo_company.objects.all().order_by('-id'),
        'count_comp':contar_companys()
    }
    return render(request, 'card_companys.html', dic)

def contar_companys():
    type_company = Tipo_company.objects.all().order_by('-id')
    count_comp = {}
    for t_companys in type_company:
        count_comp[t_companys.name] = Company.objects.filter(category_id = int(t_companys.id)).count()
    return count_comp

def getType(id_type):
    try:
        companys = Tipo_company.objects.get(id=int(id_type))
    except:
        companys = {'name':"company"}
    return companys

def getCity(id_ciudad):
    try:
        ciudad = Ciudad.objects.get(id=int(id_ciudad))
    except:
        ciudad = {'name':"Cochabamba"}
    return ciudad

def registro_company(request):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return redirect('/')
    form_user = RegisterForm()
    form_company = formCompany()
    planes = Plataforma.objects.filter(ilimitado=False).order_by('-id')
    dic = {
        'form_user':form_user,
        'form_company':form_company,
        'planes':planes
        }
    return render(request, 'registro_company.html' , dic)

def crearNuevaTienda(request, id_usuario):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return redirect('/')
    form_company = formCompany()
    planes = Plataforma.objects.all().order_by('-id')
    dic = {
        'form_company':form_company,
        'planes':planes
        }
    return render(request, 'crearNuevaTienda.html' , dic)

def validar_form(request):
    if request.method == "POST":
        formulario = formCompany(data=request.POST)
        if formulario.is_valid():
            return JsonResponse({'formulario':True})
        else:
            return JsonResponse({'error':formulario.errors})

def validar_username(request):
    if request.method == "POST":
        if User.objects.filter(email = request.POST['email']).exists():
            menj = "La cuenta: "+"<span style='color:green;'>"+request.POST['email']+"</span>"+" ya existe "
            return JsonResponse({'error':menj})
        else:
            return JsonResponse({'valido':'valido'})

def login_user(request):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return redirect('/')
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'],password=request.POST['password'])
            if user is not None:
                login(request, user)
                return JsonResponse({'user_id':int(user.id)})
            else:
                return JsonResponse({'error':'Contactese con el administrador para resolver el problema gracias.'})
        else:
            return JsonResponse({'error':'Datos incorrectos intente nuevamente gracias.'})
    
    form = AuthenticationForm()
    dic = {'form':form}
    return render(request, 'form_login.html', dic)

def salir(request):
    logout(request)
    return redirect('/')

def get_img_plan(request, id_plan):
    img = get_object_or_404(Plataforma, id = id_plan)
    #print(img.qr_img)retorna la ruta de la imagen como cadena
    return HttpResponse(json.dumps(str(img.qr_img)))

def create_mail(user_mail, subject, template_name, context):
    template = get_template(template_name)
    content = template.render(context)

    message = EmailMultiAlternatives(
        subject=subject,
        body='',
        from_email=settings.EMAIL_HOST_USER,
        to=[user_mail]
    )

    message.attach_alternative(content, 'text/html')
    return message

def send_welcome_mail(user, password, url_tienda):
    mail = create_mail(
        user,
        'Bienvenido a la plataforma AMCEB',
        'notificaciones/welcome_user_email.html',
        {
            'username': user,
            'password':password,
            'ruta':url_tienda
        }
    )
    mail.send(fail_silently=False)

def datos_registro(request):
    if request.method == "POST":
        datos = request.POST['valores']
        #print(datos)
        """ print(datos)#{user_data: {…}, company_data: {…}, plan_data: {…}}
        print(type(datos))#como string
        print("*"*50)"""
        datos = ast.literal_eval(datos)
        #print(datos)#como dict
        #print(type(datos))#como string
        user = User()
        user.username = datos['user_data']['user'].strip()
        user.email = datos['user_data']['email'].strip()
        user.password1 = user.set_password(datos['user_data']['pass1'].strip())
        user.password2 = user.set_password(datos['user_data']['pass2'].strip())
        user.save()
        
        company = Company()
        company.name = datos['company_data']['name']
        company.description = datos['company_data']['description']
        company.ruc = datos['company_data']['ruc']
        company.mobile = datos['company_data']['mobile']
        company.category_id = datos['company_data']['category']
        company.cuidad_id = datos['company_data']['cuidad']
        company.user_id = int(user.id)
        #company.image =  datos['company_data']['image']#no se puedo guardar la imagen
        company.is_service = datos['company_data']['is_service']
        company.moneda = datos['company_data']['moneda']
        company.plan_id = datos['plan_data']['plan_name']
        company.expiration_date = datetime.now().date() + timedelta(days=7)
        company.save()

        user = authenticate(username=datos['user_data']['user'].strip(),password=datos['user_data']['pass1'].strip())
        if user:
            login(request, user)
            url_tienda = 'www.amceb.online/',user.id,'/catalogo'
            user = request.user
            thread = threading.Thread(target=send_welcome_mail, args=(datos['user_data']['email'].strip(),datos['user_data']['pass1'].strip(),f"{url_tienda[0].rstrip('/')}/{url_tienda[1]}{url_tienda[2]}",))
            thread.start()

            return JsonResponse({'user_id':user.id})
        else:
            return JsonResponse({'error':"Up! ocurrio un problema, intentalo nuevamente gracias."})
        #else:
            #return JsonResponse({'error': 'Up. algo salio mal intentalo nuevamente gracias.'})

def new_store(request):
    if request.method == "POST" and request.user.is_authenticated:
        datos = request.POST['valores']
        #print(datos)
        """ print(datos)#{user_data: {…}, company_data: {…}, plan_data: {…}}
        print(type(datos))#como string
        print("*"*50)"""
        datos = ast.literal_eval(datos)
        #print(datos)#como dict
        #print(type(datos))#como string
        
        company = Company()
        company.name = datos['company_data']['name']
        company.description = datos['company_data']['description']
        company.ruc = datos['company_data']['ruc']
        company.mobile = datos['company_data']['mobile']
        company.category_id = datos['company_data']['category']
        company.cuidad_id = datos['company_data']['cuidad']
        company.user_id = int(request.user.id)
        #company.image =  datos['company_data']['image']#no se puedo guardar la imagen
        company.is_service = datos['company_data']['is_service']
        company.moneda = datos['company_data']['moneda']
        company.plan_id = datos['plan_data']['plan_name']
        company.expiration_date = datetime.now().date() + timedelta(days=7)
        company.save()
        url_tienda = 'www.amceb.online/',request.user.id,'/catalogo'
        thread = threading.Thread(target=send_welcome_mail, args=(request.user, "******", f"{url_tienda[0].rstrip('/')}/{url_tienda[1]}{url_tienda[2]}",))
        thread.start()

        return JsonResponse({'user_id':request.user.id})
    else:
        return JsonResponse({'error':"Up! ocurrio un error. inicie sesion con su usuario"})
    #else:
        #return JsonResponse({'error': 'Up. algo salio mal intentalo nuevamente gracias.'})

def contar_productos(id_user):
    companys = Company.objects.filter(user_id = int(id_user))
    count_productos = {}
    for c in companys:
        count_productos[c.name] = Product.objects.filter(company_id = int(c.id)).count()
    return count_productos

@login_required(login_url='/')
def companys_from_user(request, user_id=None):
    companys = Company.objects.filter(user_id = int(request.user.id))
    dic = {
        'companys':companys,
        'dashboard':get_Dashboard(),
        'count_productos':contar_productos(int(request.user.id))
    }
    return render(request, 'card_companys.html', dic)

@login_required(login_url='/')
def redirigir_a_companys(request):
    return redirect(f'/{request.user.id}/companys/')

def updateCompany(request, id_company):
    company = Company.objects.get(id=id_company)
    if request.method=='POST':
        form=formCompanyImage(request.POST, request.FILES,instance=company)
        if form.is_valid():
            form.save()
            return JsonResponse({'companys_from_user':request.user.id})
    else:
        form=formCompanyImage(instance=company)
        return render(request,'updateCompany.html',{'form':form,'company':company})

def add_images_company(request, id_company):
    company = Company.objects.get(id=id_company)
    if request.method == 'POST':
        form = CompanyPortadaLogoForm(request.POST,request.FILES,instance=company)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'companys_from_user': request.user.id})

    else:
        form = CompanyPortadaLogoForm(instance=company)
        return render(request,'add_images_company.html',{'form': form,'company': company})
    
def create_dominio(request, id_company):
    company = get_object_or_404(Company, id=id_company)
    # Recuperamos o creamos un dominio temporal
    try:
        dominio = company.dominio
    except Dominio.DoesNotExist:
        base_slug = slugify(company.name)
        slug = base_slug
        contador = 1
        while Dominio.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{contador}"
            contador += 1
        # Creamos y guardamos el dominio por defecto
        dominio = Dominio.objects.create(company=company, slug=slug)
    if request.method == 'POST':
        form = formCompanyDominio(request.POST, instance=dominio)
        if form.is_valid():
            dominio = form.save()
            full_url = request.build_absolute_uri(f'/{dominio.slug}/')
            return JsonResponse({
                'companys_from_user': request.user.id,
                'url': full_url,
                'slug': dominio.slug
            })
        else:
            return JsonResponse({'error': form.errors})
    else:
        form = formCompanyDominio(instance=dominio)

    # URL inicial para mostrar en el input del formulario
    initial_url = request.build_absolute_uri(f'/{dominio.slug}/')

    return render(request, 'create_dominio.html', {
        'form': form,
        'company': company,
        'initial_url': initial_url  # enviamos al template
    })

def redirigir_a_catalogo(request, slug):
    # Buscamos el dominio que coincida con el slug
    dominio = get_object_or_404(Dominio, slug=slug)
    # Redirigimos a la URL interna de la company
    # Por ejemplo, "/<id>/catalogo/"
    return redirect(f'/{dominio.company.id}/catalogo')

def deleteCompany(request, id_company):
    company = get_object_or_404(Company, id=int(id_company))
    if request.method == 'POST':
        company.delete()
        return JsonResponse({'companys_from_user':request.user.id})
    return render(request,'deleteCompany.html',{'company':company})

def add_huvicacion(request, id_company):
    company = Company.objects.get(id=id_company)
    try:  
        if request.method == 'POST':
            form = FormHuvicacion(request.POST, instance=company)
            ubicacion = Sucursal()
            ubicacion.company_id = int(id_company)
            ubicacion.address = request.POST['address']
            ubicacion.latitud = request.POST['latitud']
            ubicacion.longitud = request.POST['longitud']
            ubicacion.save()
            return JsonResponse({'success':'Registro exitoso.'})
    except:
        return JsonResponse({'error':'Ys existe el registro.'})

def info_address_company(request, id_company):
    address = Sucursal.objects.get(company_id = int(id_company))
    return render(request,'notificaciones/info_address_company.html',{'address':address})

def del_address_comp(request, id_address):
    address = get_object_or_404(Sucursal, id = int(id_address))
    id_company = address.company_id
    if request.method == 'POST':
        address.delete()
        return JsonResponse({'success':"Se Borro el registro.",'id_company':id_company})
    return render(request, 'notificaciones/del_addres_company.html', {'address':address})

@login_required(login_url='/')
def configuraciones_company(request, id_company):
    pedidos = Orden.objects.filter(company_id=int(id_company)).values('client_id').order_by('-id').distinct()
    ped = []
    for p in pedidos:
        if not p in ped:
            ped.append(p)

    productos = Product.objects.filter(stock__gt=0, company_id=int(id_company)).order_by('-id')
    dic = {
        'form_huvicacion':FormHuvicacion(),
        'form_ban':FormBanco(),
        'form_precio':PrecioForm(),
        'form_avisos':Form_avisos(),
        'form_regla':Form_condiciones(),
        'categorias':categorys_from_productos(productos),
        'company':get_company(id_company, request.user),  # ya hace validación y 404
        'total_compra':sum(item['cantidad'] for item in request.session['compra']),
        'precio':get_precio_envios(id_company),
        'avisos':Aviso.objects.filter(company_id = int(id_company))[:1],
        'banco':Banco.objects.filter(company_id = int(id_company))[:1],
        'reglas':Condicion.objects.filter(company_id = int(id_company))[:1],
        #'precio_env':determinarPrecioEnvio(id_company),distinct()
        #'ordens':Orden.objects.filter(company_id=int(id_company)).values('client_id').order_by('-id').distinct(),
        'ordens':ped,
        'clientes':Client.objects.all().order_by('-id'),
        'address':get_address(id_company),
        'form_cupom':FormCupon(),
        'cupom':Cupon.objects.filter(company_id = int(id_company))[:1]
    }
    return render(request,'configuraciones_company.html', dic)

def get_precio_envios(id_company):
    try:
        precio = Precio_envio.objects.get(company_id = int(id_company))
    except:
        precio = False
    return precio

def precio_envio(request, id_company):
    company = get_object_or_404(Company, id = int(id_company))
    if request.method == 'POST':
        form_precio = PrecioForm(request.POST, instance=company)
        if form_precio.is_valid():
            preci = Precio_envio()
            preci.precio = request.POST['precio']
            preci.precio_ciudad = request.POST['precio_ciudad']
            preci.company_id = company.id
            preci.save()
            return JsonResponse({'success':'Registro Exitoso.', 'precio':preci.precio,'precio_ciudad':preci.precio_ciudad, 'id_precio':preci.id})
        else:
            return JsonResponse({'error':'El dato no es válido.'})

def buscar_orden(request, id_company):
    if request.method == 'POST':
        pedidos = None
        cod = int(request.POST['codigo_orden'])
        if Orden.objects.filter(id=cod, company_id=int(id_company)).exists():
            orden = Orden.objects.get(id=cod)
            pedidos = Pedido.objects.filter(orden_id = orden.id)
            precio_envio = int(orden.total)  - int(orden.subtotal)
        else:
            orden, precio_envio = None, None
        return render(request, 'reportes/buscar_orden.html', {'orden':orden, 'pedidos':pedidos, 'precio_envio':precio_envio})

def reportByRange(request, id_company):
    if request.method == 'POST':
        print(request.POST['startDate'], type(request.POST['startDate']))
        inicio = datetime.strptime(request.POST['startDate'], '%d-%m-%Y')
        #print(datetime.strftime(inicio, '%Y-%m-%d')) 
        final = datetime.strptime(request.POST['endDate'], '%d-%m-%Y')
        ordenes = Orden.objects.filter(company_id = int(id_company), date_joined__range=(datetime.strftime(inicio, '%Y-%m-%d'), datetime.strftime(final, '%Y-%m-%d')))
        return render(request, 'reportes/reportByRangeOrden.html', {'ordenes':ordenes})

def inventarioProductos(request, id_company):
    criterio = request.POST.get('criterio', 'todos')

    productos = Product.objects.filter(company_id=id_company).select_related('category').annotate(
        stock_actual=ExpressionWrapper(F('stock') - F('salida'), output_field=IntegerField())
    )

    if criterio == "con_stock":
        productos = productos.filter(stock_actual__gt=0)
    elif criterio == "agotados":  # aquí corregí el nombre
        productos = productos.filter(stock_actual__lte=0)

    return render(
        request,
        'reportes/inventarioProductos.html',
        {
            'criterio': criterio,
            'id_company': id_company,
            'productos': productos.order_by('category__name', '-id'),
        },
    )

def reporte_form(request, id_company, criterio):
    form = formProducto()
    
    return render(request, "reportes/reporte_form.html", {
        "company_id":id_company,
        "form": form,
        "criterio":criterio
    })

def reporte_inventario(request, id_company, criterio):
    if request.method == 'GET':
        seleccionados = [key for key, value in request.GET.items() if value == "on"]

        # Atributos que siempre deben estar incluidos
        por_defecto = ["image", "name", "stock_actual"]

        # Aseguramos que estén incluidos en la lista final
        for attr in por_defecto:
            if attr not in seleccionados:
                seleccionados.append(attr)

        # Reordenar para que los atributos por defecto estén al principio
        seleccionados.sort(key=lambda x: (x not in por_defecto, x))

        # Base queryset con stock_actual calculado
        productos = Product.objects.filter(company_id=id_company).select_related('category').annotate(
            stock_actual=ExpressionWrapper(F('stock') - F('salida'), output_field=IntegerField())
        )

        if criterio == "con_stock":
            productos = productos.filter(stock_actual__gt=0)
        elif criterio == "agotados":   # corregido: coincide con el select del formulario
            productos = productos.filter(stock_actual__lte=0)

        # Renderizar reporte
        dic = {
            'productos': productos.order_by('category__name', '-id'),
            'seleccionados': seleccionados
        }
        html = render_to_string("reportes/reporte_inventario_pdf.html", dic)
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "inline; filename=reporte_inventario.pdf"
        font_config = FontConfiguration()
        HTML(string=html).write_pdf(response, font_config=font_config)
        return response

def add_avisos(request, id_company):
    company = get_object_or_404(Company, id = int(id_company))
    if request.method == 'POST':
        form_aviso = Form_avisos(request.POST, instance=company)
        if form_aviso.is_valid():
            a = Aviso()
            a.company_id = company.id
            a.Tiempo_entrega = request.POST['Tiempo_entrega']
            a.envios = request.POST['envios']
            a.pedidos = request.POST['pedidos']
            a.pide_ahora = request.POST['pide_ahora']
            a.save()
            return JsonResponse({'success':'Registro Exitoso.', 'avisos':a.toJSON()})
        else:
            return JsonResponse({'error':'Error intente nuevamente.'})

def get_opciones(request, id_company):
    avisos = Aviso.objects.filter(company_id = int(id_company))
    return render(request, 'notificaciones/get_opciones.html', {'avisos':avisos})

def del_precio(request, id_precio):
    precio = get_object_or_404(Precio_envio, id = int(id_precio))
    if request.method == 'POST':
        precio.delete()
        return JsonResponse({'success':"Se Borro el registro. "})
    return render(request, 'notificaciones/del_precio.html', {'precio':precio})

def banco_envio(request, id_company):
    company = get_object_or_404(Company, id = int(id_company))
    if request.method == 'POST':
        
        form_ban = FormBanco(request.POST, request.FILES)
        if form_ban.is_valid():
            formulario = form_ban.save(commit=False)
            formulario.company_id = company.id
            formulario.save()
            return JsonResponse({'success':'Registro Exitoso.'})
        else:
            return JsonResponse({'error':'Error intente nuevamente.'})

def infor_banco(request, id_company):
    banco = Banco.objects.filter(company_id = int(id_company))
    return render(request, 'notificaciones/infor_banco.html', {'banco':banco})

def del_infor_banco_by_company(request, id_banco):
    banco = get_object_or_404(Banco, id = int(id_banco))
    if request.method == 'POST':
        banco.delete()
        return JsonResponse({'success':"Se Borro el registro. "})
    return render(request, 'notificaciones/del_infor_banco_by_company.html', {'banco':banco})

def eliminar_opciones(request, id_aviso):
    aviso = get_object_or_404(Aviso, id = int(id_aviso))
    if request.method == 'POST':
        aviso.delete()
        return JsonResponse({'success':"Se Borro el registro. "})
    return render(request, 'notificaciones/eliminar_opciones.html', {'aviso':aviso})

def print_orden(request, id_company, id_orden):
    tipo = request.GET.get('tipo', 'ticket')  # 👈 por defecto ticket

    try:
        orden = Orden.objects.select_related('company', 'client').get(
            id=id_orden,
            company_id=id_company
        )
    except Orden.DoesNotExist:
        raise Http404("Orden no encontrada")

    pedidos = Pedido.objects.filter(orden=orden)
    sucursal = get_address(id_company)

    precio_envio = orden.total - orden.subtotal
    context = {
        'orden': orden,
        'company': orden.company,
        'pedidos': pedidos,
        'precio_envio': precio_envio,
        'sucursal': sucursal,
    }
    # Elegir template según tipo
    if tipo == 'factura':
        template = "reportes/report_order_pdf.html"
    else:
        template = "reportes/ticket_pdf.html"

    html = render_to_string(template, context, request=request)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{tipo}_orden_{orden.id}.pdf"'

    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)
    return response

def like_company(request, id_company, id_orden, id_cliente):
    if request.method == 'POST':
        lik = Like()
        lik.like = int(request.POST['like'])
        lik.company_id = int(id_company)
        lik.client_id = int(id_cliente)
        lik.orden_id = int(id_orden)
        lik.save()
        ruta = "/"+str(id_company)+"/catalogo" 
        print(ruta)
        return JsonResponse({'success':'Muchas gracias por su preserencia','ruta:':ruta})
    else:
        if Like.objects.filter(company_id=id_company, orden_id=id_orden, client_id=id_cliente).exists():
            ruta = str(id_company)+"/catalogo"
            dic = {
                'categorias':categorys_from_productos(productosDeCatalogo(request, id_company)),
                'total_compra':sum(item['cantidad'] for item in request.session['compra']),
                't_pago':calcular_pago(request),
                'company':get_company(id_company),
                'aviso':optener_avisos_by_company(id_company),
                'id_orden':id_orden,
                'id_cliente':id_cliente,
                'like':'Muchas gracias por su preferencia',
                'ruta:':ruta,
                'address':get_address(id_company)
            }
            return render(request, 'notificaciones/like_company.html', dic)

        else:

            dic = {
                'categorias':categorys_from_productos(productosDeCatalogo(request, id_company)),
                'productos':productosDeCatalogo(request, id_company),
                'total_compra':sum(item['cantidad'] for item in request.session['compra']),
                't_pago':calcular_pago(request),
                'company':get_company(id_company),
                'aviso':optener_avisos_by_company(id_company),
                'id_orden':id_orden,
                'id_cliente':id_cliente,
                'address':get_address(id_company)
            }
            return render(request, 'notificaciones/like_company.html', dic)


def productosDeCatalogo(request ,id_company):
    productos = Product.objects.filter(stock__gt=0, company_id=int(id_company)).order_by('-id')
    page = request.GET.get('page',1)
    try: 
        paginator = Paginator(productos, 10)
        productos = paginator.page(page)
    except:
        raise Http404
    return productos

def add_condiciones(request, id_company):
    company = get_object_or_404(Company, id = int(id_company))
    try:  
        if request.method == 'POST':
            form = Form_condiciones(request.POST, instance=company)
            c = Condicion()
            c.company_id = int(id_company)
            c.regla = request.POST['regla']
            c.save()
            return JsonResponse({'success':'Registro exitoso.'})
    except:
        return JsonResponse({'error':'Ya existe el registro.'})

def get_condiciones(request, id_company):
    try:
        reglas = Condicion.objects.filter(company_id = int(id_company))
    except:
        reglas = False
    return render(request, 'notificaciones/get_condiciones.html', {'reglas':reglas})

def delete_regla(request, id_regla):
    regla = get_object_or_404(Condicion, id = int(id_regla))
    if request.method == 'POST':
        regla.delete()
        return JsonResponse({'success':"Se Borro el registro. "})
    return render(request, 'notificaciones/delete_reglas.html', {'regla':regla})

def send_suscripcion_mail(email_user, url_tienda, company):
    mail = create_mail_suscripcion(
        email_user,
        'Bienvenido a ' + company.name.title(),
        'notificaciones/sucripcion_user_email.html',
        {
            'email_user': email_user,
            'url_tienda':url_tienda,
            'company':company
        }
    )
    mail.send(fail_silently=False)

def create_mail_suscripcion(user_mail, subject, template_name, context):
    template = get_template(template_name)
    content = template.render(context)

    message = EmailMultiAlternatives(
        subject=subject,
        body='',
        from_email=settings.EMAIL_HOST_USER,
        to=[user_mail]
    )

    message.attach_alternative(content, 'text/html')
    return message

def suscribirse(request, id_company):
    company = get_object_or_404(Company, id = int(id_company))
    url_tienda = f'https://{request.get_host()}/{id_company}/catalogo'
    try:  
        if request.method == 'POST':
            c = Suscripcion()
            c.company_id = int(id_company)
            c.email = request.POST['email']
            c.save()
            thread = threading.Thread(target=send_suscripcion_mail, args=(request.POST['email'].strip(),url_tienda, company))
            thread.start()
            return JsonResponse({'success':'¡Gracias por suscribirte! Revisa tu correo(spam), te enviamos un código de cupón para tu compra.'})
    except:
        return JsonResponse({'error':'El email ya está suscrito.'})
    
def add_cupon(request, id_company):
    company = get_object_or_404(Company, id = int(id_company))
    try:  
        if request.method == 'POST':
            form = FormCupon(request.POST, instance=company)
            c = Cupon()
            c.codigo = request.POST['codigo'].strip()
            c.descuento = int(request.POST['descuento'])
            c.company_id = int(id_company)
            c.save()
            return JsonResponse({'success':'Registro exitoso.'})
    except:
        return JsonResponse({'error':'Ya existe el registro.'})
    
def get_cupom(request, id_company):
    try:
        cupom = Cupon.objects.filter(company_id = int(id_company))
    except:
        cupom = False
    return render(request, 'notificaciones/get_cupom.html', {'cupom':cupom})

def delete_cupom(request, id_cupom):
    cupom = get_object_or_404(Cupon, id = int(id_cupom))
    if request.method == 'POST':
        cupom.delete()
        return JsonResponse({'success':"Se Borro el registro. "})
    return render(request, 'notificaciones/delete_cupom.html', {'cupom':cupom})

def redirigir_tienda(request, slug):
    # Busca el Dominio que coincida con el slug
    dominio_company = get_object_or_404(Dominio, slug=slug)
    # Si quieres mostrar la tienda dentro de tu sistema
    return redirect(f"/{dominio_company.id}/catalogo")

def estadoCompany(request, id_company):
    company = get_object_or_404(Company, id=id_company)
    try:
        slug = company.dominio.slug
        initial_url = request.build_absolute_uri(f'/{slug}/')
    except Dominio.DoesNotExist:
        initial_url = request.build_absolute_uri(f'/{company.id}/catalogo')
    return render(request, 'notificaciones/estadoCompany.html',{'company':company, 'initial_url':initial_url})

def autorizar_orden(request, id_orden):
    orden = get_object_or_404(Orden, id=id_orden)

    # 🔒 Si ya está autorizada, no volver a procesar
    if orden.status:
        return render(
            request,
            'notificaciones/orden_autorizada.html',
            {'orden': orden}
        )

    if request.method == 'POST':
        # Marcar la orden como autorizada
        orden.status = True
        orden.save()

        # Actualizar salidas de productos con F expressions
        pedidos = Pedido.objects.filter(orden=orden).select_related('product')
        for pedido in pedidos:
            producto = pedido.product
            if not producto.is_service:
                Product.objects.filter(id=producto.id).update(salida=F('salida') + pedido.cant)

        messages.success(request, "La orden fue autorizada y las salidas actualizadas correctamente.")
        return render(
            request,
            'notificaciones/orden_autorizada.html',
            {'orden': orden}
        )

    return render(
        request,
        'notificaciones/autorizar_orden.html',
        {'orden': orden}
    )