from django.forms import ModelForm

from app.catalog.models import *

class ClientFormOrder(ModelForm):
    class Meta:
        model = Client
        fields = ['names','dni','mobile']