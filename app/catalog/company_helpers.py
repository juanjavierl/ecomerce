from django.http import Http404
from django.shortcuts import get_object_or_404

from app.catalog.models import Company


def get_company(user=None):
    """Única empresa del sitio (single-tenant)."""
    company = Company.objects.first()
    if company is None:
        raise Http404('Tienda no configurada')
    return company


def get_company_id():
    return get_company().pk


def assign_company(instance):
    """Asigna la empresa única a un modelo con FK company."""
    instance.company_id = get_company_id()
    return instance
