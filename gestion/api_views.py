# gestion/api_views.py

from rest_framework import viewsets, filters, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Vuelo, Avion
# NOTA: Esta importación ya es correcta según tu serializers.py
from .serializers import VueloSerializer, AvionSerializer 
from .permissions import IsAdminOrReadOnly, IsAdminRole, IsPasajeroRole
# Asegúrate de importar los permisos específicos

# -------------------------------------
# 1. GESTIÓN DE AVIONES (CRUD Admin)
# -------------------------------------

class AvionViewSet(viewsets.ModelViewSet):
    queryset = Avion.objects.all()
    serializer_class = AvionSerializer
    # Solo el Admin tiene acceso de escritura (y lectura para todos autenticados)
    permission_classes = [IsAdminOrReadOnly] 


# -------------------------------------
# 2. GESTIÓN DE VUELOS (CRUD Admin + Filtrado)
# -------------------------------------

# NOTA: El nombre de la clase es VueloViewSet (sin 'API')
class VueloViewSet(viewsets.ModelViewSet):
    queryset = Vuelo.objects.all().order_by('fecha_salida')
    serializer_class = VueloSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['origen', 'destino']
    search_fields = ['origen', 'destino', 'codigo_vuelo']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Lógica de visibilidad: 
        # Si NO es Admin, solo muestra vuelos futuros y programados.
        if not user.is_admin:
             queryset = queryset.filter(
                 fecha_salida__gte=timezone.now(),
                 estado=Vuelo.Estado.PROGRAMADO
             )

        # Filtro por fecha (ej: ?fecha=YYYY-MM-DD)
        fecha = self.request.query_params.get('fecha')
        if fecha:
            queryset = queryset.filter(fecha_salida__date=fecha)
            
        return queryset

    # Endpoint para cambiar el estado del vuelo (POST, solo Admin)
    # URL: /api/vuelos/{pk}/cambiar_estado/
    @action(detail=True, methods=['post'], permission_classes=[IsAdminRole]) # Usa el permiso de Rol
    def cambiar_estado(self, request, pk=None):
        vuelo = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        estados_validos = Vuelo.Estado.values
        if nuevo_estado not in estados_validos:
            return Response(
                {'error': f'Estado inválido. Use uno de: {estados_validos}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        vuelo.estado = nuevo_estado
        vuelo.save()
        return Response({'status': f'Estado de vuelo cambiado a {vuelo.get_estado_display()}'})