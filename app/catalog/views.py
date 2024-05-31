#importamos todos lo modulos de propios de django
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse, request
from django.core.paginator import Paginator
from django.views.generic import DeleteView, CreateView, UpdateView, TemplateView,DetailView
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.http import Http404
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
    form = form_cliente()

    return render(request, 'catalog/confirmar_pedido.html',{'form':form})