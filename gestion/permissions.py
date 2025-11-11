# gestion/permissions.py

from rest_framework import permissions
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS
# Obtenemos el modelo de usuario para verificar el tipo de objeto
Usuario = get_user_model() 
from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    """
    Permite acceso solo a usuarios que sean staff o superusuario.
    """
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)


class IsPasajeroRole(BasePermission):
    """
    Permite acceso solo a usuarios NO administradores (pasajeros).
    """
    def has_permission(self, request, view):
        return request.user and not request.user.is_staff and not request.user.is_superuser

        
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