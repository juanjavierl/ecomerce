from django.http import Http404

from app.catalog.models import Company


def get_company(user=None):
    """Unica empresa del sitio (single-tenant)."""
    company = Company.objects.first()
    if company is None:
        raise Http404('Tienda no configurada')
    return company


def assign_company(instance):
    return instance
