from django.core.management.base import BaseCommand
from usuarios.models import Rol

class Command(BaseCommand):
    help = 'Agrega el rol de entrenador al sistema'

    def handle(self, *args, **kwargs):
        rol, created = Rol.objects.get_or_create(
            nombre=Rol.ENTRENADOR,
            defaults={'descripcion': 'Encargado del entrenamiento y preparación de los caballos'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Rol "Entrenador" creado'))
        else:
            self.stdout.write(f'- Rol "Entrenador" ya existe')