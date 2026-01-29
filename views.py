from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Caballo, ClaseEntrenamiento, ControlVeterinario, PerfilUsuario, Rol, TareaPetisero
from django.db.models import Q
from django.utils import timezone

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        if not nombre or not username or not password:
            messages.error(request, 'Todos los campos son obligatorios')
            return render(request, 'usuarios/register.html')
        
        if len(nombre) < 2:
            messages.error(request, 'El nombre debe tener al menos 2 caracteres')
            return render(request, 'usuarios/register.html')
        
        if len(username) < 3:
            messages.error(request, 'El usuario debe tener al menos 3 caracteres')
            return render(request, 'usuarios/register.html')
        
        if len(password) < 4:
            messages.error(request, 'La contraseña debe tener al menos 4 caracteres')
            return render(request, 'usuarios/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'usuarios/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe')
            return render(request, 'usuarios/register.html')
        
        try:
            user = User.objects.create_user(username=username, password=password, first_name=nombre)
            perfil = PerfilUsuario.objects.create(user=user)
            perfil.agregar_rol(Rol.CLIENTE)
            login(request, user)
            messages.success(request, f'¡Bienvenido {nombre}! Tu cuenta ha sido creada exitosamente')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, 'Error al crear la cuenta. Intenta de nuevo')
            return render(request, 'usuarios/register.html')
    
    return render(request, 'usuarios/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Por favor ingresa usuario y contraseña')
            return render(request, 'usuarios/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            nombre = user.first_name if user.first_name else username
            messages.success(request, f'¡Bienvenido de vuelta {nombre}!')
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, 'usuarios/login.html')
    
    return render(request, 'usuarios/login.html')

def logout_view(request):
    if request.method == 'POST':
        nombre = request.user.first_name if request.user.first_name else request.user.username
        logout(request)
        messages.success(request, f'Hasta pronto {nombre}. Has cerrado sesión exitosamente')
        return redirect('home')
    return redirect('home')

@login_required
def dashboard_view(request):
    perfil, created = PerfilUsuario.objects.get_or_create(user=request.user)
    if created:
        perfil.agregar_rol(Rol.CLIENTE)
    
    rol_activo = request.session.get('rol_activo', Rol.CLIENTE)
    
    context = {
        'perfil': perfil,
        'roles': perfil.roles.all(),
        'rol_activo': rol_activo
    }
    
    if rol_activo in [Rol.VETERINARIO, Rol.PETISERO, Rol.ENTRENADOR]:
        buscar = request.GET.get('buscar', '')
        caballos = Caballo.objects.filter(activo=True)
        
        if buscar:
            caballos = caballos.filter(
                Q(nombre__icontains=buscar) | 
                Q(raza__icontains=buscar) |
                Q(propietario__username__icontains=buscar)
            )
        
        context['caballos'] = caballos
        context['buscar'] = buscar
    
    templates = {
        Rol.VETERINARIO: 'usuarios/dashboard_veterinario.html',
        Rol.PETISERO: 'usuarios/dashboard_petisero.html',
        Rol.ADMINISTRADOR: 'usuarios/dashboard_administrador.html',
        Rol.CLIENTE: 'usuarios/dashboard_cliente.html',
        Rol.ENTRENADOR: 'usuarios/dashboard_entrenador.html',
    }
    
    template = templates.get(rol_activo, 'usuarios/dashboard_cliente.html')
    return render(request, template, context)

@login_required
def cambiar_rol_view(request, rol_nombre):
    perfil = PerfilUsuario.objects.get(user=request.user)
    
    if perfil.tiene_rol(rol_nombre):
        request.session['rol_activo'] = rol_nombre
        messages.success(request, f'Vista cambiada a {Rol.objects.get(nombre=rol_nombre).get_nombre_display()}')
    else:
        messages.error(request, 'No tienes acceso a este rol')
    
    return redirect('dashboard')

@login_required
def caballo_detail_view(request, caballo_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.VETERINARIO):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    caballo = Caballo.objects.get(id=caballo_id)
    controles = caballo.controles.all()
    
    return render(request, 'usuarios/caballo_detail.html', {
        'caballo': caballo,
        'controles': controles
    })

@login_required
def control_nuevo_view(request, caballo_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.VETERINARIO):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    caballo = Caballo.objects.get(id=caballo_id)
    
    if request.method == 'POST':
        peso = request.POST.get('peso')
        condicion_corporal = request.POST.get('condicion_corporal')
        alimentacion = request.POST.get('alimentacion')
        observaciones = request.POST.get('observaciones', '')
        
        if not peso or not condicion_corporal or not alimentacion:
            messages.error(request, 'Completa todos los campos requeridos')
            return render(request, 'usuarios/control_nuevo.html', {'caballo': caballo})
        
        ControlVeterinario.objects.create(
            caballo=caballo,
            veterinario=request.user,
            peso=peso,
            condicion_corporal=condicion_corporal,
            alimentacion=alimentacion,
            observaciones=observaciones
        )
        
        messages.success(request, 'Control registrado exitosamente')
        return redirect('caballo_detail', caballo_id=caballo_id)
    
    return render(request, 'usuarios/control_nuevo.html', {'caballo': caballo})

@login_required
def petisero_caballo_detail_view(request, caballo_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.PETISERO):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    caballo = Caballo.objects.get(id=caballo_id)
    controles = caballo.controles.all()
    tareas = caballo.tareas_petisero.filter(fecha__date=timezone.now().date()).first()
    
    return render(request, 'usuarios/petisero_caballo_detail.html', {
        'caballo': caballo,
        'controles': controles,
        'tareas': tareas
    })

@login_required
def petisero_checklist_view(request, caballo_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.PETISERO):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    caballo = Caballo.objects.get(id=caballo_id)
    hoy = timezone.now().date()
    tareas = caballo.tareas_petisero.filter(fecha__date=hoy).first()
    
    if tareas:
        messages.warning(request, 'Ya registraste las tareas de hoy para este caballo')
        return redirect('petisero_caballo_detail', caballo_id=caballo_id)
    
    if request.method == 'POST':
        TareaPetisero.objects.create(
            caballo=caballo,
            petisero=request.user,
            limpieza_cascos=request.POST.get('limpieza_cascos') == 'on',
            revision_herraduras=request.POST.get('revision_herraduras') == 'on',
            tratamiento_cascos=request.POST.get('tratamiento_cascos') == 'on',
            aplicacion_aceite=request.POST.get('aplicacion_aceite') == 'on',
            revision_herraje=request.POST.get('revision_herraje') == 'on',
            medicacion=request.POST.get('medicacion') == 'on',
            limpieza_heridas=request.POST.get('limpieza_heridas') == 'on',
            ejercicios_prescritos=request.POST.get('ejercicios_prescritos') == 'on',
            observaciones=request.POST.get('observaciones', '')
        )
        
        messages.success(request, 'Tareas registradas exitosamente')
        return redirect('petisero_caballo_detail', caballo_id=caballo_id)
    
    return render(request, 'usuarios/petisero_checklist.html', {'caballo': caballo})

@login_required
def admin_usuarios_view(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ADMINISTRADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    buscar = request.GET.get('buscar', '')
    usuarios = User.objects.all()
    
    if buscar:
        usuarios = usuarios.filter(
            Q(username__icontains=buscar) | 
            Q(first_name__icontains=buscar) |
            Q(email__icontains=buscar)
        )
    
    return render(request, 'usuarios/admin_usuarios.html', {
        'usuarios': usuarios,
        'buscar': buscar
    })

@login_required
def admin_usuario_crear_view(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ADMINISTRADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Usuario y contraseña son obligatorios')
            return render(request, 'usuarios/admin_usuario_form.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe')
            return render(request, 'usuarios/admin_usuario_form.html')
        
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=nombre,
            email=email
        )
        PerfilUsuario.objects.create(user=user)
        
        messages.success(request, f'Usuario {username} creado exitosamente')
        return redirect('admin_usuarios')
    
    return render(request, 'usuarios/admin_usuario_form.html')

@login_required
def admin_usuario_editar_view(request, user_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ADMINISTRADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    usuario = get_object_or_404(User, id=user_id)
    perfil_usuario, created = PerfilUsuario.objects.get_or_create(user=usuario)
    
    if request.method == 'POST':
        usuario.first_name = request.POST.get('nombre', '').strip()
        usuario.email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if password:
            usuario.set_password(password)
        
        usuario.save()
        messages.success(request, f'Usuario {usuario.username} actualizado')
        return redirect('admin_usuarios')
    
    return render(request, 'usuarios/admin_usuario_form.html', {
        'usuario': usuario,
        'editar': True
    })

@login_required
def admin_usuario_eliminar_view(request, user_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ADMINISTRADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    usuario = get_object_or_404(User, id=user_id)
    
    if usuario.id == request.user.id:
        messages.error(request, 'No puedes eliminarte a ti mismo')
        return redirect('admin_usuarios')
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario {username} eliminado')
        return redirect('admin_usuarios')
    
    return render(request, 'usuarios/admin_usuario_eliminar.html', {'usuario': usuario})

@login_required
def admin_usuario_roles_view(request, user_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ADMINISTRADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    usuario = get_object_or_404(User, id=user_id)
    perfil_usuario, created = PerfilUsuario.objects.get_or_create(user=usuario)
    todos_roles = Rol.objects.all()
    
    if request.method == 'POST':
        roles_seleccionados = request.POST.getlist('roles')
        perfil_usuario.roles.clear()
        
        for rol_id in roles_seleccionados:
            rol = Rol.objects.get(id=rol_id)
            perfil_usuario.roles.add(rol)
        
        messages.success(request, f'Roles de {usuario.username} actualizados')
        return redirect('admin_usuarios')
    
    return render(request, 'usuarios/admin_usuario_roles.html', {
        'usuario': usuario,
        'perfil_usuario': perfil_usuario,
        'todos_roles': todos_roles
    })

@login_required
def admin_caballos_view(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ADMINISTRADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    buscar = request.GET.get('buscar', '')
    caballos = Caballo.objects.all()
    
    if buscar:
        caballos = caballos.filter(
            Q(nombre__icontains=buscar) | 
            Q(raza__icontains=buscar) |
            Q(propietario__username__icontains=buscar)
        )
    
    return render(request, 'usuarios/admin_caballos.html', {
        'caballos': caballos,
        'buscar': buscar
    })

@login_required
def admin_caballo_crear_view(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ADMINISTRADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    usuarios = User.objects.all()
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        raza = request.POST.get('raza', '').strip()
        edad = request.POST.get('edad')
        color = request.POST.get('color', '').strip()
        propietario_id = request.POST.get('propietario')
        
        if not nombre or not edad or not propietario_id:
            messages.error(request, 'Nombre, edad y propietario son obligatorios')
            return render(request, 'usuarios/admin_caballo_form.html', {'usuarios': usuarios})
        
        propietario = User.objects.get(id=propietario_id)
        
        Caballo.objects.create(
            nombre=nombre,
            raza=raza,
            edad=edad,
            color=color,
            propietario=propietario
        )
        
        messages.success(request, f'Caballo {nombre} creado exitosamente')
        return redirect('admin_caballos')
    
    return render(request, 'usuarios/admin_caballo_form.html', {'usuarios': usuarios})

@login_required
def admin_caballo_editar_view(request, caballo_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ADMINISTRADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    caballo = get_object_or_404(Caballo, id=caballo_id)
    usuarios = User.objects.all()
    
    if request.method == 'POST':
        caballo.nombre = request.POST.get('nombre', '').strip()
        caballo.raza = request.POST.get('raza', '').strip()
        caballo.edad = request.POST.get('edad')
        caballo.color = request.POST.get('color', '').strip()
        caballo.propietario = User.objects.get(id=request.POST.get('propietario'))
        caballo.activo = request.POST.get('activo') == 'on'
        
        caballo.save()
        messages.success(request, f'Caballo {caballo.nombre} actualizado')
        return redirect('admin_caballos')
    
    return render(request, 'usuarios/admin_caballo_form.html', {
        'caballo': caballo,
        'usuarios': usuarios,
        'editar': True
    })

@login_required
def admin_caballo_eliminar_view(request, caballo_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ADMINISTRADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    caballo = get_object_or_404(Caballo, id=caballo_id)
    
    if request.method == 'POST':
        nombre = caballo.nombre
        caballo.delete()
        messages.success(request, f'Caballo {nombre} eliminado')
        return redirect('admin_caballos')
    
    return render(request, 'usuarios/admin_caballo_eliminar.html', {'caballo': caballo})

@login_required
def admin_caballo_historial_view(request, caballo_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ADMINISTRADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    caballo = get_object_or_404(Caballo, id=caballo_id)
    controles = caballo.controles.all()
    tareas = caballo.tareas_petisero.all()
    
    return render(request, 'usuarios/admin_caballo_historial.html', {
        'caballo': caballo,
        'controles': controles,
        'tareas': tareas
    })

@login_required
def entrenador_clases_view(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ENTRENADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    filtro = request.GET.get('filtro', 'todas')
    
    clases = ClaseEntrenamiento.objects.filter(entrenador=request.user)
    
    if filtro == 'pendientes':
        clases = clases.filter(estado=ClaseEntrenamiento.PENDIENTE)
    elif filtro == 'completadas':
        clases = clases.filter(estado=ClaseEntrenamiento.COMPLETADA)
    elif filtro == 'canceladas':
        clases = clases.filter(estado=ClaseEntrenamiento.CANCELADA)
    
    return render(request, 'usuarios/entrenador_clases.html', {
        'clases': clases,
        'filtro': filtro
    })

@login_required
def entrenador_clase_completar_view(request, clase_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ENTRENADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    clase = get_object_or_404(ClaseEntrenamiento, id=clase_id, entrenador=request.user)
    
    if clase.estado != ClaseEntrenamiento.PENDIENTE:
        messages.error(request, 'Esta clase ya fue procesada')
        return redirect('entrenador_clases')
    
    if request.method == 'POST':
        clase.estado = ClaseEntrenamiento.COMPLETADA
        clase.observaciones = request.POST.get('observaciones', clase.observaciones)
        clase.save()
        
        messages.success(request, 'Clase marcada como completada')
        return redirect('entrenador_clases')
    
    return render(request, 'usuarios/entrenador_clase_completar.html', {'clase': clase})

@login_required
def entrenador_clase_cancelar_view(request, clase_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ENTRENADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    clase = get_object_or_404(ClaseEntrenamiento, id=clase_id, entrenador=request.user)
    
    if clase.estado != ClaseEntrenamiento.PENDIENTE:
        messages.error(request, 'Esta clase ya fue procesada')
        return redirect('entrenador_clases')
    
    if request.method == 'POST':
        clase.estado = ClaseEntrenamiento.CANCELADA
        clase.save()
        
        messages.success(request, 'Clase cancelada exitosamente')
        return redirect('entrenador_clases')
    
    return render(request, 'usuarios/entrenador_clase_cancelar.html', {'clase': clase})

@login_required
def entrenador_clase_reprogramar_view(request, clase_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.ENTRENADOR):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    clase = get_object_or_404(ClaseEntrenamiento, id=clase_id, entrenador=request.user)
    
    if clase.estado != ClaseEntrenamiento.PENDIENTE:
        messages.error(request, 'Solo puedes reprogramar clases pendientes')
        return redirect('entrenador_clases')
    
    if request.method == 'POST':
        nueva_fecha = request.POST.get('fecha')
        nueva_hora_inicio = request.POST.get('hora_inicio')
        nueva_hora_fin = request.POST.get('hora_fin')
        
        if not nueva_fecha or not nueva_hora_inicio or not nueva_hora_fin:
            messages.error(request, 'Todos los campos son obligatorios')
            return render(request, 'usuarios/entrenador_clase_reprogramar.html', {'clase': clase})
        
        conflicto = ClaseEntrenamiento.objects.filter(
            entrenador=request.user,
            fecha=nueva_fecha,
            estado=ClaseEntrenamiento.PENDIENTE
        ).filter(
            Q(hora_inicio__lt=nueva_hora_fin, hora_fin__gt=nueva_hora_inicio)
        ).exclude(id=clase_id).exists()
        
        if conflicto:
            messages.error(request, 'Ya tienes una clase en ese horario')
            return render(request, 'usuarios/entrenador_clase_reprogramar.html', {'clase': clase})
        
        clase.fecha = nueva_fecha
        clase.hora_inicio = nueva_hora_inicio
        clase.hora_fin = nueva_hora_fin
        clase.save()
        
        messages.success(request, 'Clase reprogramada exitosamente')
        return redirect('entrenador_clases')
    
    return render(request, 'usuarios/entrenador_clase_reprogramar.html', {'clase': clase})

@login_required
def cliente_reservas_view(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.CLIENTE):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    mis_reservas = ClaseEntrenamiento.objects.filter(cliente=request.user).order_by('-fecha', '-hora_inicio')
    
    return render(request, 'usuarios/cliente_reservas.html', {
        'reservas': mis_reservas
    })

@login_required
def cliente_nueva_reserva_view(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.CLIENTE):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    entrenadores = User.objects.filter(perfil__roles__nombre=Rol.ENTRENADOR)
    caballos = Caballo.objects.filter(activo=True)
    horarios = ClaseEntrenamiento.horarios_disponibles()
    
    if request.method == 'POST':
        entrenador_id = request.POST.get('entrenador')
        caballo_id = request.POST.get('caballo')
        fecha = request.POST.get('fecha')
        horario = request.POST.get('horario')
        tipo_entrenamiento = request.POST.get('tipo_entrenamiento')
        
        if not all([entrenador_id, caballo_id, fecha, horario, tipo_entrenamiento]):
            messages.error(request, 'Completa todos los campos')
            return render(request, 'usuarios/cliente_nueva_reserva.html', {
                'entrenadores': entrenadores,
                'caballos': caballos,
                'horarios': horarios
            })
        
        hora_inicio, hora_fin = horario.split('-')
        
        conflicto = ClaseEntrenamiento.objects.filter(
            entrenador_id=entrenador_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            estado=ClaseEntrenamiento.PENDIENTE
        ).exists()
        
        if conflicto:
            messages.error(request, 'Ese horario ya está reservado con ese entrenador')
            return render(request, 'usuarios/cliente_nueva_reserva.html', {
                'entrenadores': entrenadores,
                'caballos': caballos,
                'horarios': horarios
            })
        
        ClaseEntrenamiento.objects.create(
            entrenador_id=entrenador_id,
            cliente=request.user,
            caballo_id=caballo_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            tipo_entrenamiento=tipo_entrenamiento
        )
        
        messages.success(request, 'Reserva creada exitosamente')
        return redirect('cliente_reservas')
    
    return render(request, 'usuarios/cliente_nueva_reserva.html', {
        'entrenadores': entrenadores,
        'caballos': caballos,
        'horarios': horarios
    })

@login_required
def cliente_cancelar_reserva_view(request, clase_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not perfil.tiene_rol(Rol.CLIENTE):
        messages.error(request, 'No tienes acceso a esta sección')
        return redirect('dashboard')
    
    clase = get_object_or_404(ClaseEntrenamiento, id=clase_id, cliente=request.user)
    
    if clase.estado != ClaseEntrenamiento.PENDIENTE:
        messages.error(request, 'No puedes cancelar esta reserva')
        return redirect('cliente_reservas')
    
    if request.method == 'POST':
        clase.estado = ClaseEntrenamiento.CANCELADA
        clase.save()
        messages.success(request, 'Reserva cancelada exitosamente')
        return redirect('cliente_reservas')
    
    return render(request, 'usuarios/cliente_cancelar_reserva.html', {'clase': clase})