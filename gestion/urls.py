from django.urls import path
from . import views

urlpatterns = [
    # PÚBLICO / PASAJERO
    path('', views.ListaVuelosView.as_view(), name='vuelos_disponibles'),
    path('vuelos/<int:pk>/', views.detalle_vuelo_view, name='detalle_vuelo'),
    path('vuelos/<int:vuelo_pk>/reservar/', views.crear_reserva_view, name='crear_reserva'),

    # RESERVAS
    path('reservas/<int:pk>/detalle/', views.reserva_detalle_view, name='reserva_detalle'),
    path(
        'reservas/<int:reserva_pk>/boleto/pdf/',
        views.boleto_pdf_view,
        name='boleto_pdf'
    ),
    path(
        'reservas/<int:reserva_pk>/asientos/',
        views.seleccionar_asiento_view,
        name='seleccionar_asiento'
    ),

    # PANEL ADMIN VUELOS
    path('panel/vuelos/', views.VueloAdminListView.as_view(), name='vuelos_admin_list'),
    path('panel/vuelos/nuevo/', views.VueloCreateView.as_view(), name='vuelo_crear'),
    path('panel/vuelos/<int:pk>/editar/', views.VueloUpdateView.as_view(), name='vuelo_editar'),
    path('panel/vuelos/<int:pk>/eliminar/', views.VueloDeleteView.as_view(), name='vuelo_eliminar'),

    # AUTENTICACIÓN
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),

    # PERFIL
    path('perfil/', views.perfil_view, name='perfil'),
]
