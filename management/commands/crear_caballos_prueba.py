from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import Caballo

class Command(BaseCommand):
    help = 'Crea caballos de prueba'

    def handle(self, *args, **kwargs):
        user = User.objects.first()
        
        caballos = [
            {'nombre': 'Thunder', 'raza': 'Pura Sangre', 'edad': 5, 'color': 'Marrón'},
            {'nombre': 'Luna', 'raza': 'Cuarto de Milla', 'edad': 7, 'color': 'Negro'},
            {'nombre': 'Rayo', 'raza': 'Andaluz', 'edad': 4, 'color': 'Blanco'},
            {'nombre': 'Estrella', 'raza': 'Criollo', 'edad': 6, 'color': 'Zaino'},
            {'nombre': 'Trueno', 'raza': 'Árabe', 'edad': 3, 'color': 'Gris'},
        ]
        
        for data in caballos:
            caballo, created = Caballo.objects.get_or_create(
                nombre=data['nombre'],
                defaults={**data, 'propietario': user}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Caballo "{caballo.nombre}" creado'))
            else:
                self.stdout.write(f'- Caballo "{caballo.nombre}" ya existe')