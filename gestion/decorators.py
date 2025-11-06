# gestion/decorators.py

from django.contrib.auth.decorators import user_passes_test

def is_admin_check(user):
    """Verifica si el usuario es un administrador usando la propiedad is_admin."""
    # Usamos la propiedad del modelo Usuario que incluye superusuarios
    return user.is_authenticated and user.is_admin

admin_required = user_passes_test(is_admin_check, login_url='/login/')