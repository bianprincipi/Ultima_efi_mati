# aerolinea/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Asegúrate de que estas importaciones sean correctas (o usa api_views)
from gestion import views 
from gestion import api_views as api 

# Configuración del Router de DRF
router = DefaultRouter()
router.register(r'vuelos', api.VueloAPIViewSet, basename='vuelos-api') 
# ... otros router.register si existen ...

urlpatterns = [
    # Rutas de administración y autenticación
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), 
    
    # Rutas de la API (DRF)
    path('api/v1/', include(router.urls)), 
    
    # 💥 LA SOLUCIÓN AL 404: Incluir las URLs de la aplicación principal en la raíz 💥
 path('', include('your_app_name.urls')), ## Asigna gestion.urls a la URL raíz ('')
]