# aerolinea/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import LogoutView

from gestion import api_views as api
from gestion.api_views import (
    PasajerosPorVueloReport,
    ReservasActivasPorPasajeroReport,
)

router = routers.DefaultRouter()
router.register(r'vuelos', api.VueloViewSet, basename='vuelos')
router.register(r'aviones', api.AvionViewSet, basename='aviones')
router.register(r'pasajeros', api.PasajeroViewSet, basename='pasajeros')
router.register(r'reservas', api.ReservaViewSet, basename='reservas')
router.register(r'boletos', api.BoletoViewSet, basename='boletos')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Web (HTML)
    path('', include('gestion.urls')),

    # API REST
    path('api/', include(router.urls)),

    # Auth Token
    path('api/auth/', obtain_auth_token, name='api_token_auth'),

    # Reportes
    path('api/reportes/pasajeros-por-vuelo/', PasajerosPorVueloReport.as_view(),
         name='reporte_pasajeros_por_vuelo'),
    path('api/reportes/reservas-activas/', ReservasActivasPorPasajeroReport.as_view(),
         name='reporte_reservas_activas'),

    # Logout HTML
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
