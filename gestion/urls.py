# gestion/urls.py

from django.urls import path
from django.contrib.auth.views import LogoutView 
from django.views.generic import TemplateView
from . import views 

# Namespace de la aplicación (ayuda a prevenir colisiones de nombres: gestion:nombre_url)
app_name = 'gestion' 

urlpatterns = [
    # =================================================================
    # 1. VISTAS PÚBLICAS / HOME
    # =================================================================
    
    # HOME - Lista de vuelos para el público
    path('', views.ListaVuelosView.as_view(), name='vuelos_disponibles'),
    
    # =================================================================
    # 2. VISTAS DE AUTENTICACIÓN
    # =================================================================

    # Login
    path('login/', views.login_view, name='login'), 
    
    # Registro 
    path('registro/', views.registro_view, name='registro'),
    
    # Perfil (Usando TemplateView como placeholder)
    path('perfil/', TemplateView.as_view(template_name='gestion/perfil.html'), name='perfil'),
    
    # Cierre de Sesión (Logout)
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    
    # =================================================================
    # 3. VISTAS DE GESTIÓN HTML (CRUD ADMIN)
    # =================================================================

    # CRUD de Vuelos
    path('admin/vuelos/', views.VueloAdminListView.as_view(), name='vuelos_admin_list'),
    
    # Vuelo Crear (¡CORREGIDO: usa .as_view()!)
    path('admin/vuelos/crear/', views.VueloCreateView.as_view(), name='vuelo_crear'), 
    
    path('admin/vuelos/editar/<int:pk>/', views.VueloUpdateView.as_view(), name='vuelo_editar'),
    path('admin/vuelos/eliminar/<int:pk>/', views.VueloDeleteView.as_view(), name='vuelo_eliminar'),
    
    # =================================================================
    # 4. VISTAS DE RESERVA Y PASAJERO
    # =================================================================

    # Detalle del Vuelo
    path('vuelos/<int:pk>/detalle/', views.detalle_vuelo_view, name='detalle_vuelo'),
    
    # Creación de Reserva (paso 1)
    path('vuelos/<int:vuelo_pk>/reservar/', views.crear_reserva_view, name='crear_reserva'),
    
    # Selección de Asiento (paso 2)
    path('reserva/<int:reserva_pk>/asiento/', views.seleccionar_asiento_view, name='seleccionar_asiento'),
    
    # Detalle/Confirmación de Reserva
    path('reserva/<int:pk>/', views.reserva_detalle_view, name='reserva_detalle'),
]