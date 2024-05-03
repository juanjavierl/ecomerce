from django.shortcuts import render, HttpResponse
from django.http import JsonResponse, request
from django.views.generic import DeleteView, CreateView, UpdateView, TemplateView,DetailView
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from app.catalog.models import *
# Create your views here.
class CatalogView(TemplateView):
    template_name = "index.html" 
    def get(self, request, *args, **kwargs):
        try:
            request.session['compra']
        except:
            request.session['compra'] = []
        dic = {
            'categorias':Category.objects.all().order_by('-id'),
            'productos':Product.objects.all(),
            'total_compra':len(request.session['compra']),
            'total_pago':0
        }
        
        return render(request,self.template_name, dic)

def optenerProducto(request, id_producto):
    p = Product.objects.get(id = id_producto)
    datos = {}
    dic = {}
    data_cli = request.session['compra']
    if request.method == 'POST':
        datos['id_producto'] = int(p.id)
        datos['name'] = p.name
        datos['cantidad'] = int(request.POST['cantidad'])
        datos['precio_uni'] = float(p.price)
        datos['total'] = float(int(request.POST['cantidad']) * float(p.price))
        if not datos in data_cli:
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
        else:
            dic['error'] = "Ya ingreso el Producto"
            return JsonResponse(dic)

        
        
    
    return render(request,'catalog/OptenerProducto.html',{'p':p})

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
    productos = Product.objects.filter(category = id_categoria)
    return render(request, 'card_productos.html', {'productos':productos})