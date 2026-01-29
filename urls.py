from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('cambiar-rol/<str:rol_nombre>/', views.cambiar_rol_view, name='cambiar_rol'),
    
    path('veterinario/caballo/<int:caballo_id>/', views.caballo_detail_view, name='caballo_detail'),
    path('veterinario/control/nuevo/<int:caballo_id>/', views.control_nuevo_view, name='control_nuevo'),
    
    path('petisero/caballo/<int:caballo_id>/', views.petisero_caballo_detail_view, name='petisero_caballo_detail'),
    path('petisero/checklist/<int:caballo_id>/', views.petisero_checklist_view, name='petisero_checklist'),
    
    path('gestion/usuarios/', views.admin_usuarios_view, name='admin_usuarios'),
    path('gestion/usuario/crear/', views.admin_usuario_crear_view, name='admin_usuario_crear'),
    path('gestion/usuario/<int:user_id>/editar/', views.admin_usuario_editar_view, name='admin_usuario_editar'),
    path('gestion/usuario/<int:user_id>/eliminar/', views.admin_usuario_eliminar_view, name='admin_usuario_eliminar'),
    path('gestion/usuario/<int:user_id>/roles/', views.admin_usuario_roles_view, name='admin_usuario_roles'),
    
    path('gestion/caballos/', views.admin_caballos_view, name='admin_caballos'),
    path('gestion/caballo/crear/', views.admin_caballo_crear_view, name='admin_caballo_crear'),
    path('gestion/caballo/<int:caballo_id>/editar/', views.admin_caballo_editar_view, name='admin_caballo_editar'),
    path('gestion/caballo/<int:caballo_id>/eliminar/', views.admin_caballo_eliminar_view, name='admin_caballo_eliminar'),
    path('gestion/caballo/<int:caballo_id>/historial/', views.admin_caballo_historial_view, name='admin_caballo_historial'),

    path('entrenador/clases/', views.entrenador_clases_view, name='entrenador_clases'),
    path('entrenador/clase/<int:clase_id>/completar/', views.entrenador_clase_completar_view, name='entrenador_clase_completar'),
    path('entrenador/clase/<int:clase_id>/cancelar/', views.entrenador_clase_cancelar_view, name='entrenador_clase_cancelar'),
    path('entrenador/clase/<int:clase_id>/reprogramar/', views.entrenador_clase_reprogramar_view, name='entrenador_clase_reprogramar'),

    path('cliente/reservas/', views.cliente_reservas_view, name='cliente_reservas'),
    path('cliente/reserva/nueva/', views.cliente_nueva_reserva_view, name='cliente_nueva_reserva'),
    path('cliente/reserva/<int:clase_id>/cancelar/', views.cliente_cancelar_reserva_view, name='cliente_cancelar_reserva'),
]