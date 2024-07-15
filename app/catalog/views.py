#importamos todos lo modulos de propios de django
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse, request
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.views.generic import DeleteView, CreateView, UpdateView, TemplateView,DetailView
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.http import Http404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate,login, logout
#importamos modulos de terceros


#importamos los modelos de nuestra aplicacion
from app.catalog.models import *
from app.catalog.forms import *
# Create your views here.
class CatalogView(TemplateView):
    template_name = "index.html" 
    def get(self, request, *args, **kwargs):

        productos = Product.objects.all()
        try:
            page = request.GET.get('page',1)
            paginator = Paginator(productos,2)
            productos = paginator.page(page)
        except:
            raise Http404

        try:
            request.session['compra']
        except:
            request.session['compra'] = []

        
        dic = {
            'categorias':Category.objects.all().order_by('-id'),
            'productos':productos,
            'entity':productos,
            'page':page,
            'paginator':paginator,
            'total_compra':len(request.session['compra']),
            'total_pago':0,
            'company':get_company()
        }
        
        return render(request,self.template_name, dic)

def get_company():
    try:
        company = Company.objects.all()[0]
    except:
        company = 'Compania'
    return company

def optenerProducto(request, id_producto):
    p = get_object_or_404(Product, id=id_producto)
    datos = {}
    dic = {}
    data_cli = request.session['compra']
    if request.method == 'POST':
        if not request.POST['cantidad'].isdigit():
            return JsonResponse({'error':"La cantidad debe ser mayor a cero"})
        if int(request.POST['cantidad']) > p.stock:
            menj = "La cantidad Maxima disponible es: ",p.stock
            return JsonResponse({'error':menj})
        print("el cliente envio la informacion")
        datos['id_producto'] = int(p.id)
        datos['name'] = p.name
        datos['cantidad'] = int(request.POST['cantidad'])
        datos['precio_uni'] = float(p.price)
        datos['total'] = float(int(request.POST['cantidad']) * float(p.price))
        if len(data_cli) == 0:#cuando el carrio esta vacio
            data_cli.append(datos)
            request.session['compra'] = data_cli
            dic = {
                'total_compra':len(request.session['compra']),
                'cantidad':int(request.POST['cantidad']),
                'producto':p.name.title(),
                'precio_uni':float(p.price),
                'total':float(int(request.POST['cantidad']) * float(p.price)),
                'datos': request.session['compra'],
                "total_pago":0
            }
            dic['success'] = "Producto Registrado"
            return JsonResponse(dic)
        elif len(data_cli) > 0:#si el producto ya existe en la variable data_cli entonces buscar
            for indice in range(0,len(data_cli),1):
                if datos['id_producto'] == data_cli[indice]['id_producto']:
                    data_cli[indice]['cantidad'] = int(data_cli[indice]['cantidad']) + int(datos['cantidad'])
                    data_cli[indice]['total'] = float(data_cli[indice]['cantidad'] * float(p.price))
                    data_cli[indice] = data_cli[indice]
                    request.session['compra'] = data_cli
                    dic['success'] = "Se actualizo su compra"
                    return JsonResponse(dic)
            #si el producto es diferente a los demas entonces agrgar a la session
            if not datos in data_cli:
                data_cli.append(datos)
                request.session['compra'] = data_cli
                
                dic['success'] = "Producto Registrado"
                dic['total_compra'] = len(request.session['compra'])
                return JsonResponse(dic)
        

    return render(request,'catalog/OptenerProducto.html',{
                    'p':p,
                    'total_compra':len(request.session['compra']),
                    'company':get_company()
                    }
                )

def ver_carrito(request):
    datos = request.session['compra']
    t_pago = calcular_pago(request)
    #print(datos)

    return render(request, 'catalog/ver_carrito.html',{'datos':datos,'t_pago':t_pago})

def calcular_pago(request):
    print(request.session['compra'])
    total_pago = 0
    productos = request.session['compra']
    for producto in productos:
        total_pago += float(producto['total'])
    return total_pago

def vaciar_carrito(request):
    request.session['compra'] = []
    return HttpResponse(len(request.session['compra']))

def eliminarProducto(request, id_producto):#el id_producto es el indicen 
    productos = request.session['compra']
    productos.pop(int(id_producto))
    request.session['compra'] = productos
    return HttpResponse(len(request.session['compra']))

@csrf_exempt
def shear_product(request):
    if request.method=="POST":
        print("post")
        texto=request.POST["search"]
        busqueda=(
            Q(name=texto) |
            Q(description__icontains=texto) |
            Q(code__icontains=texto)
        )
        resultados=Product.objects.filter(busqueda).distinct()
        return render(request,'catalog/shear_product.html',{'datos':resultados})
    else:
        texto=request.GET["search"]
        busqueda=(
            Q(name__icontains=texto) |
            Q(description__icontains=texto) |
            Q(code__icontains=texto)
        )
        resultados=Product.objects.filter(busqueda).distinct()
        return render(request,'catalog/shear_product.html',{'datos':resultados})

"""
select *
from Product
whire id_categoria = {{id_categoria}}
"""
def mostrar_por_categoria(request, id_categoria):
    productos = Product.objects.filter(category_id = id_categoria)
    return render(request, 'catalog/card_productos.html', {'productos':productos})

def confirmar_pedido(request):
    if request.method == 'POST':
        if not request.POST['dni'].isdigit():
            return JsonResponse({'error': "El Nro de Nit/CI debe ser numérico."})
        if not request.POST['mobile'].isdigit():
            return JsonResponse({'error': "El Nro de Celular debe ser numérico."})
        
        forms=ClientFormOrder(request.POST)
        try:#si ya existe ese cliente
            print("ya existe ese cliente")
            cliente = Client.objects.get(dni = int(request.POST['dni']))
            orden = crear_orden(cliente.id)#se crea una orden
            for productos in request.session['compra']:#[{'id_producto':12,'cantidad':1},{'id_producto':10,'cantidad':2}]
                pedido = Pedido()
                pedido.orden_id = int(orden.id)
                pedido.product_id = int(productos['id_producto'])
                pedido.cant = int(productos['cantidad'])
                pedido.price = float(productos['precio_uni'])
                pedido.total = float(int(productos['cantidad']) * float(productos['precio_uni']))
                pedido.save()
            lista_product = request.session['compra']
            t_pago = calcular_pago(request)
            request.session['compra'] = []#cuando al cliente confirma su pedido se resetea al carrito a 0
            return JsonResponse(
                        {
                            'company':orden.company.name,
                            'cliente':orden.client.names,
                            'lugar':lugar,
                            'cel_company':orden.company.mobile,
                            'products':len(request.session['compra']),
                            'success':"Bien, tu pedido a sido registrado. <a href='/'> Ir al Inicio</a>",
                            'lista':lista_product,#envio lasession en la variable lista_product
                            't_pago':t_pago
                        }
                    )
        except Client.DoesNotExist:
            print("NO existe ese cliente")
            if forms.is_valid():
                cliente = forms.save(commit=False)
                cliente.save()
                orden = crear_orden(cliente.id)
                for productos in request.session['compra']:#[{'id_producto':12,'cantidad':1},{'id_producto':10,'cantidad':2}]
                    pedido = Pedido()
                    pedido.orden_id = int(orden.id)
                    pedido.product_id = int(productos['id_producto'])
                    pedido.cant = int(productos['cantidad'])
                    pedido.price = float(productos['precio_uni'])
                    pedido.total = float(int(productos['cantidad']) * float(productos['precio_uni']))
                    pedido.save()
                t_pago = calcular_pago(request)
                lista_product = request.session['compra']
                request.session['compra'] = []#cuando al cliente confirma su pedido se resetea al carrito a 0
                return JsonResponse(
                            {
                                'company':orden.company.name,
                                'cel_company':orden.company.mobile,
                                'cliente':orden.client.names,
                                'lugar':lugar,
                                'products':len(request.session['compra']),
                                'success':"En hora buena realizaste tu pedido.<a href='/'> Ir al Inicio</a>",
                                'lista':lista_product,
                                't_pago':t_pago
                            }
                        )
    dic = {
        'form':ClientFormOrder(),
        'total_compra':len(request.session['compra']),
        'company':get_company(),
        'categorias':Category.objects.all(),
        'datos':request.session['compra'],
         "t_pago":calcular_pago(request)
    }
    return render(request,'catalog/confirmar_pedido.html',dic)

def crear_orden(id_cliente):
    orden = Orden()
    orden.client_id = int(id_cliente)
    orden.company_id = int(get_company().id)
    orden.total = float(calcular_pago(request))
    orden.save()
    return orden

def login_user(request):
    if request.method == "POST":
        form_user = AuthenticationForm(data=request.POST)
        if form_user.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                print("TE AUTENTICASTE EN EL SISTEMA")
                login(request, user)
                return JsonResponse({'login':"login"})
            else:
                return JsonResponse({'error':'Error, Contactese con el administrador para resolver el problema gracias.'})
        else:
            return JsonResponse({'error':'Error, datos incorrectos intente nuevamente gracias.'})
    else:
        form_user = AuthenticationForm()
        dic = {'form_user':form_user}
    return render(request, 'usuarios/login.html', dic)

def salir(request):
    logout(request)
    return redirect('/')