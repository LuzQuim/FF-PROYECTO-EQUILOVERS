from django.contrib import admin
from .models import Caballo, ClaseEntrenamiento, ControlVeterinario, Rol, PerfilUsuario, TareaPetisero

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'telefono', 'fecha_creacion', 'mostrar_roles']
    list_filter = ['roles', 'fecha_creacion']
    search_fields = ['user__username', 'user__first_name', 'telefono']
    filter_horizontal = ['roles']
    
    def mostrar_roles(self, obj):
        return ", ".join([rol.get_nombre_display() for rol in obj.roles.all()])
    mostrar_roles.short_description = 'Roles'

@admin.register(Caballo)
class CaballoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'raza', 'edad', 'propietario', 'activo']
    list_filter = ['activo', 'raza']
    search_fields = ['nombre', 'propietario__username']

@admin.register(ControlVeterinario)
class ControlVeterinarioAdmin(admin.ModelAdmin):
    list_display = ['caballo', 'veterinario', 'fecha', 'peso', 'condicion_corporal']
    list_filter = ['fecha', 'condicion_corporal']
    search_fields = ['caballo__nombre', 'veterinario__username']

@admin.register(TareaPetisero)
class TareaPetiseroAdmin(admin.ModelAdmin):
    list_display = ['caballo', 'petisero', 'fecha', 'limpieza_cascos', 'revision_herraduras']
    list_filter = ['fecha']
    search_fields = ['caballo__nombre', 'petisero__username']

@admin.register(ClaseEntrenamiento)
class ClaseEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ['caballo', 'entrenador', 'cliente', 'fecha', 'hora_inicio', 'estado']
    list_filter = ['estado', 'fecha', 'tipo_entrenamiento']
    search_fields = ['caballo__nombre', 'entrenador__username', 'cliente__username']