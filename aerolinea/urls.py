# aerolinea/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers 
from gestion import api_views as api # Asumo que tienes un api_views.py en 'gestion'
from django.contrib.auth.views import LogoutView 

# Configuración del Router de Django REST Framework
router = routers.DefaultRouter()

# CORRECCIÓN DE LA API (Asumo que el nombre es VueloViewSet)
router.register(r'vuelos', api.VueloViewSet, basename='vuelos-api')
router.register(r'aviones', api.AvionViewSet, basename='aviones-api')
# Agrega aquí otros ViewSets


urlpatterns = [
    # URLs de la administración de Django
    path('admin/', admin.site.urls),
    
    # URLs de la aplicación principal 'gestion'
    path('', include('gestion.urls')),

    # URLs de la API REST
    path('api/', include(router.urls)),

    # LOGOUT GLOBAL (Necesario para el formulario en base.html)
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'), 
]