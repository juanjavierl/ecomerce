
#encoding:utf-8
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import User
from django.forms import ModelForm, widgets

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