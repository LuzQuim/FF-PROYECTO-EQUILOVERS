from django.core.management.base import BaseCommand
from usuarios.models import Rol

class Command(BaseCommand):
    help = 'Crea los roles iniciales del sistema'

    def handle(self, *args, **kwargs):
        roles = [
            (Rol.VETERINARIO, 'Encargado de la salud y cuidado de los caballos'),
            (Rol.PETISERO, 'Especialista en el cuidado de cascos y herraje'),
            (Rol.ADMINISTRADOR, 'Gestiona el sistema y usuarios'),
            (Rol.CLIENTE, 'Usuario que utiliza los servicios'),
        ]
        
        for nombre, descripcion in roles:
            rol, created = Rol.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Rol "{rol.get_nombre_display()}" creado'))
            else:
                self.stdout.write(f'- Rol "{rol.get_nombre_display()}" ya existe')