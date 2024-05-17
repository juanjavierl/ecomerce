from django.contrib import admin

# Register your models here.
from app.catalog.models import *

admin.site.register([Category,Company,Product])