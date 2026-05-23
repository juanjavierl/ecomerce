from django.db.models import Avg, Max, Min, Count
from django.http import JsonResponse, request
from django.shortcuts import render, get_object_or_404,HttpResponse,redirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import User
from django.contrib.auth import authenticate,login, logout

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.forms import SetPasswordForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.core.cache import cache
from app.inicio.models import *
from app.catalog.models import Company, Product
from .forms import *

from openai import OpenAI
# Create your views here.

def robots_txt(request):
    sitemap_url = f"https://{request.get_host()}/sitemap.xml"
    lines = [
        "User-Agent: *",
        "Disallow: /admin/",
        "Disallow: /ver_planes/",
        "Disallow: /change_password/",
        "Disallow: /login_user/",
        "Disallow: /registro_company/",
        "Allow: /",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def inicio(request):
    """Redirige al catálogo único (single-tenant)."""
    return redirect('/')

def get_Dashboard():
    try:
        dashboard = Dashboard.objects.get(id=1)
    except:
        dashboard = {'name':"AMCEB",'mobile':79436914,'codigo':''}
    return dashboard

def verPlanes(request):
    return redirect('/')

def update_perfil_user(request, user_id):
    user = get_object_or_404(User, id = int(user_id))
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success':'Datos actualizados correctamente.'})
        else:
            return JsonResponse({'error':'Error intente nuevamente.'})
    form = UpdateUserForm(instance=user)
    return render(request,'update_perfil_user.html',{'form':form})

def changePassword(request, id_user):
    if request.method=='POST':
        form=ChangePasswordForm(request.POST)
        new_password = request.POST['new_password']
        confirmed = request.POST['confirm_password']
        user = request.user
        print(user.check_password(request.POST['old_password']))
        if new_password == confirmed and user.check_password(request.POST['old_password']):
            user.set_password(new_password)
            user.save()
            print('bien')
            return JsonResponse({"success":'Bien actualizaste tus credenciales, autentificate nuevamente gracias.'})
        else:
            return JsonResponse({"error":'Los dastos son incorrectos, intente nuevamente gracias.'})
    else:
        form=ChangePasswordForm()
    return render(request,'changePassword.html',{'form':form})


class AjaxPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form.save(self.request)
            return JsonResponse({'message': 'Correo enviado con éxito'})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        return super().form_invalid(form)

def password_reset_confirm_ajax(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        return JsonResponse({'error': 'Token inválido'}, status=400)

    if not default_token_generator.check_token(user, token):
        return JsonResponse({'error': 'Token inválido o expirado'}, status=400)

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Tu contraseña fue restablecida correctamente.'})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = SetPasswordForm(user)

    return render(request, 'password_confirm.html', {'form': form})

def guardar_datos_extra(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        user.first_name = response.get('given_name', '')
        user.last_name = response.get('family_name', '')
        user.email = response.get('email', '')
        user.save()

def redirigir_a_companys(backend, user, response, *args, **kwargs):
    if user and user.is_authenticated:
        company = Company.objects.first()
        if company and company.user_id == user.id:
            return redirect('/configuraciones/')
        return redirect('/')

#client = OpenAI(api_key=settings.OPENAI_API_KEY)
@method_decorator(csrf_exempt, name='dispatch')
class ChatBotView(View):
    def post(self, request):
        user_message = request.POST.get("text_boot", "").strip()

        # Buscar productos por nombre, descripción o categoría
        productos = Product.objects.filter(
            Q(name__icontains=user_message) |
            Q(description__icontains=user_message) |
            Q(category__name__icontains=user_message)
        )
        # Preparar resultados
        productos_data = [
            {
                "name": p.name.title(),
                "price": str(p.price),
                "moneda": p.company.moneda,
                "image_url": p.image.url if p.image else "",
                "url": f"/detail_product/{p.id}/",
                "description": (p.description[:100] + "...") if p.description and len(p.description) > 80 else p.description or "",
                "ciudad": getattr(p.company, 'cuidad', '') or "---",
            }
            for p in productos
        ]

        # Intentar consultar OpenAI solo si hay productos
        """ bot_reply = ""
        if productos_data:
            productos_texto = "\n".join([f"- {p['name']} (${p['price']})" for p in productos_data])
            try:
                respuesta = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Eres un asistente de ventas de una tienda online. Responde de forma amigable y breve."},
                        {"role": "user", "content": f"El cliente dijo: {user_message}. Estos son los productos que encontré:\n{productos_texto}"},
                    ],
                )
                bot_reply = respuesta.choices[0].message.content
            except Exception:
                # Si OpenAI falla, usamos respuesta por defecto
                bot_reply = "Aquí están los productos que encontré:"
        else:
            bot_reply = "No encontré productos que coincidan con tu búsqueda."
 """
        return JsonResponse({
            #"reply": bot_reply,
            "productos": productos_data
        })
