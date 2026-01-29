from django.db import models
from django.contrib.auth.models import User

class Rol(models.Model):
    VETERINARIO = 'veterinario'
    PETISERO = 'petisero'
    ADMINISTRADOR = 'administrador'
    CLIENTE = 'cliente'
    ENTRENADOR = 'entrenador'
    
    ROLES_CHOICES = [
        (VETERINARIO, 'Veterinario'),
        (PETISERO, 'Petisero'),
        (ADMINISTRADOR, 'Administrador'),
        (CLIENTE, 'Cliente'),
        (ENTRENADOR, 'Entrenador'),
    ]
    
    nombre = models.CharField(max_length=20, choices=ROLES_CHOICES, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.get_nombre_display()

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    roles = models.ManyToManyField(Rol, related_name='usuarios')
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def tiene_rol(self, nombre_rol):
        return self.roles.filter(nombre=nombre_rol).exists()
    
    def agregar_rol(self, nombre_rol):
        rol, created = Rol.objects.get_or_create(nombre=nombre_rol)
        self.roles.add(rol)
    
    def remover_rol(self, nombre_rol):
        try:
            rol = Rol.objects.get(nombre=nombre_rol)
            self.roles.remove(rol)
        except Rol.DoesNotExist:
            pass

class Caballo(models.Model):
    nombre = models.CharField(max_length=100)
    raza = models.CharField(max_length=100, blank=True)
    edad = models.IntegerField()
    color = models.CharField(max_length=50, blank=True)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caballos')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Caballos'
    
    def __str__(self):
        return self.nombre

class ControlVeterinario(models.Model):
    caballo = models.ForeignKey(Caballo, on_delete=models.CASCADE, related_name='controles')
    veterinario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    peso = models.DecimalField(max_digits=6, decimal_places=2)
    condicion_corporal = models.IntegerField(choices=[(i, i) for i in range(1, 10)])
    alimentacion = models.TextField()
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Controles Veterinarios'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.caballo.nombre} - {self.fecha.strftime('%d/%m/%Y')}"
    
class TareaPetisero(models.Model):
    caballo = models.ForeignKey(Caballo, on_delete=models.CASCADE, related_name='tareas_petisero')
    petisero = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    limpieza_cascos = models.BooleanField(default=False)
    revision_herraduras = models.BooleanField(default=False)
    tratamiento_cascos = models.BooleanField(default=False)
    aplicacion_aceite = models.BooleanField(default=False)
    revision_herraje = models.BooleanField(default=False)
    medicacion = models.BooleanField(default=False)
    limpieza_heridas = models.BooleanField(default=False)
    ejercicios_prescritos = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Tareas Petisero'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.caballo.nombre} - {self.fecha.strftime('%d/%m/%Y')}"
    
class ClaseEntrenamiento(models.Model):
    PENDIENTE = 'pendiente'
    COMPLETADA = 'completada'
    CANCELADA = 'cancelada'
    
    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (COMPLETADA, 'Completada'),
        (CANCELADA, 'Cancelada'),
    ]
    
    entrenador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clases_entrenador')
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clases_cliente')
    caballo = models.ForeignKey(Caballo, on_delete=models.CASCADE, related_name='clases')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo_entrenamiento = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Clases de Entrenamiento'
        ordering = ['fecha', 'hora_inicio']
    
    def __str__(self):
        return f"{self.caballo.nombre} - {self.fecha} {self.hora_inicio}"
    
    @staticmethod
    def horarios_disponibles():
        return [
            ('08:00', '09:00'),
            ('09:00', '10:00'),
            ('10:00', '11:00'),
            ('11:00', '12:00'),
            ('12:00', '13:00'),
            ('14:00', '15:00'),
            ('15:00', '16:00'),
            ('16:00', '17:00'),
            ('17:00', '18:00'),
        ]