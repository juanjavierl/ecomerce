from django.forms import ModelForm

from app.catalog.models import *

class form_cliente(ModelForm):
    class Meta:
        model = Client
        fields = ['names','dni','mobile']