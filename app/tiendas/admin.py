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
admin.site.register([Banco, Sucursal,Precio_envio, Aviso, Condicion, RRSS, PixelMeta])
