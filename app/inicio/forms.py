
#encoding:utf-8
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import User
from django.forms import ModelForm, widgets

from app.catalog.models import Dashboard

from .models import *
from .forms import *

class UpdateUserForm(forms.ModelForm):
    #username = forms.CharField(max_length=140, label="Email / Usuario")
    class Meta:
        model = User
        fields = ('first_name','last_name','email')
        #exclude = ('email', 'password1', 'password2')

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=40,label="Anterior Contraseña", widget = forms.PasswordInput)
    new_password = forms.CharField(max_length=40,label="Nueva Contraseña", widget = forms.PasswordInput)
    confirm_password = forms.CharField(max_length=40,label="Repetir Nueva Contraseña", widget = forms.PasswordInput)

class formConfiguraciones(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('name','nit','description','mobile','email','address','ciudad','moneda','image','button')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'nit': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea({'class': 'form-control', 'rows': 2, 'cols': 3}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'moneda': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'button': forms.TextInput(attrs={'class': 'form-control'})
        }

class formWeb(forms.ModelForm):
    class Meta:
        model = Dashboard
        fields = ('name','author','navbar','favicon','color_texto')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}), 
            'navbar': forms.TextInput(attrs={'class': 'form-control'}),
            'color_texto': forms.TextInput(attrs={'class': 'form-control'}),
        }