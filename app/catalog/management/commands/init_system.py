from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.catalog.models import Company  # ajusta el import

class Command(BaseCommand):
    help = "Inicializa el sistema"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Crear superusuario
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin'
            )
            self.stdout.write(self.style.SUCCESS(
                "Superusuario creado."
            ))
        else:
            self.stdout.write("El superusuario ya existe.")

        # Crear empresa por defecto
        if not Company.objects.exists():
            Company.objects.create(
                name="Empresa Demo",
                mobile="70000000",
                address="Sin dirección",
                email="admin@example.com",
                ciudad="Sin ciudad",
                moneda="Bs",
                button="Nuevos productos"
            )
            self.stdout.write(self.style.SUCCESS(
                "Empresa por defecto creada."
            ))
        else:
            self.stdout.write("Ya existe una empresa.")