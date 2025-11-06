# gestion/permissions.py

from rest_framework import permissions
from django.contrib.auth import get_user_model

# Obtenemos el modelo de usuario para verificar el tipo de objeto
Usuario = get_user_model() 

class IsAdminRole(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo el acceso a usuarios con rol ADMIN.
    """
    message = 'Acceso denegado. Solo los administradores pueden realizar esta acción.'

    def has_permission(self, request, view):
        # Asegúrate de que el usuario esté autenticado
        if request.user.is_authenticated:
            # Comprueba si el usuario tiene el rol ADMIN o es un superusuario (is_superuser)
            # El superusuario (createsuperuser) debe tener acceso de Admin siempre.
            return (hasattr(request.user, 'rol') and request.user.rol == request.user.Rol.ADMIN) or request.user.is_superuser
        return False

class IsPasajeroRole(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo el acceso a usuarios con rol PASAJERO.
    """
    message = 'Acceso denegado. Solo los pasajeros pueden realizar esta acción.'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            # Comprueba si el usuario tiene el rol PASAJERO
            return hasattr(request.user, 'rol') and request.user.rol == request.user.Rol.PASAJERO
        return False
        
class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite el acceso si el usuario es Admin o si es el dueño del objeto (ej. Pasajero, Reserva).
    """
    message = 'Acceso denegado. No tienes permiso para acceder a este objeto.'
    
    def has_object_permission(self, request, view, obj):
        # Lectura (GET, HEAD, OPTIONS) siempre permitida si el usuario está autenticado, 
        # excepto si se está editando o eliminando algo que no es suyo.
        if request.method in permissions.SAFE_METHODS:
            return True

        # 1. Permiso para Admin (incluye superusuario)
        if hasattr(request.user, 'rol') and request.user.rol == request.user.Rol.ADMIN or request.user.is_superuser:
            return True
        
        # 2. Permiso para Dueño del Objeto
        
        # Caso A: El objeto es el propio Usuario (ej. GET /api/pasajeros/9/)
        if isinstance(obj, Usuario): 
            return obj == request.user
            
        # Caso B: El objeto tiene una relación 'pasajero' (ej. Reserva, Boleto)
        if hasattr(obj, 'pasajero'):
            return obj.pasajero == request.user
            
        return False

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso para lectura (GET) para todos los autenticados, y escritura solo para Admin.
    """
    def has_permission(self, request, view):
        # Lectura permitida para todos los autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Escritura (POST, PUT, DELETE) solo si es Admin
        return request.user and request.user.is_authenticated and request.user.is_admin