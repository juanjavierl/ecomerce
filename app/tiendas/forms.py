#encoding:utf-8
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import User
from django.forms.models import ModelForm
from .models import *

from django.core.exceptions import ValidationError
import phonenumbers

class RegisterForm(UserCreationForm):
    username = forms.CharField(max_length=140, label="Email / Usuario")
    class Meta:
        model = get_user_model()
        fields = ('username','email', 'password1', 'password2')

class formCompany(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True
    class Meta:
        model = Company
        exclude = ('user','website','date_joined','image', 'logo','plan', 'status', 'expiration_date')
        
    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        try:
            parsed = phonenumbers.parse(mobile, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValidationError("Número de teléfono inválido.")
        except:
            raise ValidationError("Ingrese un número válido con su código de país.")
        
        return mobile
    
#clase para actualizar la companias de los clientes
class formCompanyImage(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True
    class Meta:
        model = Company
        exclude = ('user','website','date_joined','image', 'logo','plan', 'status', 'expiration_date')

class CompanyPortadaLogoForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ('image', 'logo')

class FormHuvicacion(forms.ModelForm):
    class Meta:
        model = Sucursal
        exclude = ('date_joined','company')

class PrecioForm(forms.ModelForm):
    class Meta:
        model = Precio_envio
        exclude = ('date_joined','company')

class FormCupon(forms.ModelForm):
    descuento = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(
            attrs={
                'type': 'range',
                'min': '0',
                'max': '100',
                'step': '1',
                'class': 'form-range',  # Bootstrap class opcional
            }
        ),
        label='Ingrese el porcentaje del descuento %',
    )
    class Meta:
        model = Cupon
        exclude = ('company','estado',)

class FormBanco(forms.ModelForm):
    class Meta:
        model = Banco
        exclude = ('company',)

class Form_avisos(forms.ModelForm):
    class Meta:
        model = Aviso
        exclude = ('company',)

class Form_condiciones(forms.ModelForm):
    class Meta:
        model = Condicion
        exclude = ('company',)

    
from django import forms

class AdminEmailForm(forms.Form):
    subject = forms.CharField(label="Asunto", max_length=200)
    message = forms.CharField(label="Mensaje", widget=forms.Textarea)