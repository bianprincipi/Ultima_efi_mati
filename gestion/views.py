# gestion/views.py

from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import transaction

from .serializers import VueloSerializer, AsientoSerializer
# IMPORTACIONES NECESARIAS:
# Asegúrate de que todos estos modelos, formularios y el decorador existan
from .models import Vuelo, Asiento, Reserva # Modelos (Añade los que necesites)
from .forms import VueloAdminForm, LoginForm, RegistroForm, ReservaForm # Formularios
from .decorators import admin_required # Decorador para vistas basadas en funciones


# =================================================================
# 1. MIXIN DE PERMISOS (ADMIN)
# =================================================================

class AdminRequiredMixin(UserPassesTestMixin):
    """
    Bloquea el acceso a la vista si el usuario no es Admin.
    Usa la propiedad .is_admin del modelo Usuario.
    """
    login_url = reverse_lazy('login')

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin

# =================================================================
# 2. VISTAS PÚBLICAS / AUTENTICACIÓN
# =================================================================

# Listado de vuelos para el público/pasajero
class ListaVuelosView(ListView):
    model = Vuelo
    template_name = 'gestion/vuelos_list.html'
    context_object_name = 'vuelos'

# Login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.first_name}!")
            
            if user.is_admin:
                return redirect('vuelos_admin_list')
            return redirect('vuelos_disponibles')
        
        messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()
    
    return render(request, 'gestion/login.html', {'form': form})

# Registro
def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Cuenta creada con éxito! Bienvenido a bordo.")
            return redirect('vuelos_disponibles')
        
        messages.error(request, "Hubo un error en el registro. Revise los datos.")
    else:
        form = RegistroForm()
    
    return render(request, 'gestion/registro.html', {'form': form})


# =================================================================
# 3. VISTAS DE GESTIÓN HTML (CRUD ADMIN)
# =================================================================

# 1. LISTAR VUELOS (Admin)
class VueloAdminListView(AdminRequiredMixin, ListView):
    model = Vuelo
    template_name = 'gestion/vuelo_admin_list.html'
    context_object_name = 'vuelos'

# 2. CREAR VUELO (Admin)
class VueloCreateView(AdminRequiredMixin, CreateView):
    model = Vuelo
    form_class = VueloAdminForm
    template_name = 'gestion/vuelo_form.html' 
    success_url = reverse_lazy('vuelos_admin_list')

# 3. EDITAR VUELO (Admin)
class VueloUpdateView(AdminRequiredMixin, UpdateView):
    model = Vuelo
    form_class = VueloAdminForm
    template_name = 'gestion/vuelo_form.html'
    success_url = reverse_lazy('vuelos_admin_list')

# 4. ELIMINAR VUELO (Admin)
class VueloDeleteView(AdminRequiredMixin, DeleteView):
    model = Vuelo
    template_name = 'gestion/vuelo_confirm_delete.html'
    success_url = reverse_lazy('vuelos_admin_list') 
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, f"El vuelo {self.get_object().codigo_vuelo} ha sido eliminado correctamente.")
        return super().delete(request, *args, **kwargs)


# =================================================================
# 4. VISTAS DE RESERVA Y PASAJERO
# =================================================================

@login_required(login_url=reverse_lazy('login'))
def detalle_vuelo_view(request, pk):
    """Muestra el detalle del vuelo y opciones de reserva."""
    vuelo = get_object_or_404(Vuelo, pk=pk)
    
    context = {'vuelo': vuelo}
    return render(request, 'gestion/vuelo_detalle.html', context)


@login_required(login_url=reverse_lazy('login'))
@transaction.atomic 
def crear_reserva_view(request, vuelo_pk):
    """
    Crea una reserva inicial y redirige a la selección de asiento.
    """
    vuelo = get_object_or_404(Vuelo, pk=vuelo_pk)
    # Si ya tiene una reserva pendiente/confirmada, redirigir
    if Reserva.objects.filter(pasajero=request.user, vuelo=vuelo, estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.CONFIRMADA]).exists():
        messages.warning(request, "Ya tienes una reserva activa o pendiente para este vuelo.")
        return redirect('reserva_detalle', pk=vuelo_pk) # Asume que hay una vista de detalle de reserva

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.vuelo = vuelo
            reserva.pasajero = request.user
            reserva.estado = Reserva.Estado.PENDIENTE 
            reserva.save()
            
            messages.success(request, "Reserva inicial creada. ¡A seleccionar el asiento!")
            return redirect('seleccionar_asiento', reserva_pk=reserva.pk) 
        
        messages.error(request, "Error al crear la reserva.")
    else:
        form = ReservaForm() 
    
    context = {'form': form, 'vuelo': vuelo}
    return render(request, 'gestion/reserva_crear.html', context)


@login_required(login_url=reverse_lazy('login'))
def seleccionar_asiento_view(request, reserva_pk):
    """
    Muestra el mapa de asientos y permite al pasajero seleccionar uno.
    
    """
    reserva = get_object_or_404(Reserva, pk=reserva_pk, pasajero=request.user)
    vuelo = reserva.vuelo
    
    # --- Lógica de Disponibilidad ---
    asientos_vuelo = Asiento.objects.filter(avion=vuelo.avion).order_by('fila', 'columna')
    
    asientos_ocupados_ids = Reserva.objects.filter(
        vuelo=vuelo, 
        estado__in=[Reserva.Estado.CONFIRMADA, Reserva.Estado.PENDIENTE] 
    ).exclude(pk=reserva_pk).values_list('asiento__pk', flat=True) # Usar asiento__pk para FK

    # Crear el layout para renderizar
    layout = {}
    columnas_disponibles = set()
    for asiento in asientos_vuelo:
        if asiento.fila not in layout:
            layout[asiento.fila] = {}
        
        is_ocupado = asiento.pk in asientos_ocupados_ids
        layout[asiento.fila][asiento.columna] = {'asiento': asiento, 'ocupado': is_ocupado}
        columnas_disponibles.add(asiento.columna)

    if request.method == 'POST':
        asiento_id = request.POST.get('asiento_id')
        asiento_seleccionado = get_object_or_404(Asiento, pk=asiento_id, avion=vuelo.avion)
        
        # Comprobación final de disponibilidad
        if asiento_seleccionado.pk in asientos_ocupados_ids:
            messages.error(request, "Ese asiento fue reservado hace un instante. ¡Selecciona otro rápido!")
            return redirect('seleccionar_asiento', reserva_pk=reserva.pk)
        
        with transaction.atomic():
            reserva.asiento = asiento_seleccionado
            reserva.estado = Reserva.Estado.CONFIRMADA 
            reserva.save()
            
        messages.success(request, f"¡Asiento {asiento_seleccionado.fila}{asiento_seleccionado.columna} seleccionado! Reserva confirmada.")
        return redirect('reserva_detalle', pk=reserva.pk)

    context = {
        'vuelo': vuelo,
        'reserva': reserva,
        'layout': layout,
        'columnas': sorted(list(columnas_disponibles)) # Para iterar el encabezado
    }
    return render(request, 'gestion/asiento_selector.html', context)


@login_required(login_url=reverse_lazy('login'))
def reserva_detalle_view(request, pk):
    """
    Muestra los detalles de una reserva específica para el pasajero.
    """
    reserva = get_object_or_404(Reserva, pk=pk, pasajero=request.user)
    
    # Si la reserva no está confirmada o está pendiente, podemos redirigir al selector
    if reserva.estado == Reserva.Estado.PENDIENTE and not reserva.asiento:
        messages.warning(request, "Tu reserva está pendiente de selección de asiento.")
        return redirect('seleccionar_asiento', reserva_pk=reserva.pk)

    context = {
        'reserva': reserva,
        'vuelo': reserva.vuelo
    }
    return render(request, 'gestion/reserva_detalle.html', context)


# Nota: Necesitarás añadir todas estas rutas ('detalle_vuelo', 'crear_reserva', 'seleccionar_asiento', 'reserva_detalle') en gestion/urls.py.