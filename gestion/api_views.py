# gestion/api_views.py

from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Vuelo, Avion, Asiento, Reserva, Boleto
from .serializers import (
    VueloSerializer,
    AvionSerializer,
    AsientoSerializer,
    ReservaSerializer,
    BoletoSerializer,
    PasajeroSerializer,
)
from .permissions import IsAdminOrReadOnly
from gestion import serializers  # usamos este + permisos estándar DRF

Usuario = get_user_model()


# =====================================================
# 1. AVIONES (CRUD Admin + Layout asientos)
# =====================================================

class AvionViewSet(viewsets.ModelViewSet):
    queryset = Avion.objects.all()
    serializer_class = AvionSerializer
    permission_classes = [IsAdminOrReadOnly]

    # GET /api/aviones/{id}/layout/
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def layout(self, request, pk=None):
        avion = self.get_object()
        asientos = Asiento.objects.filter(avion=avion).order_by('fila', 'columna')
        serializer = AsientoSerializer(asientos, many=True)
        return Response(serializer.data)


# =====================================================
# 2. VUELOS (CRUD Admin + filtros + asientos)
# =====================================================

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

        # Si no es admin, solo vuelos futuros y programados
        if not (user.is_authenticated and user.is_staff):
            queryset = queryset.filter(
                fecha_salida__gte=timezone.now(),
                estado=Vuelo.Estado.PROGRAMADO
            )

        # Filtro ?fecha=YYYY-MM-DD
        fecha = self.request.query_params.get('fecha')
        if fecha:
            queryset = queryset.filter(fecha_salida__date=fecha)

        return queryset

    # POST /api/vuelos/{id}/cambiar_estado/
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def cambiar_estado(self, request, pk=None):
        vuelo = self.get_object()
        nuevo_estado = request.data.get('estado')

        if nuevo_estado not in Vuelo.Estado.values:
            return Response(
                {'error': f"Estado inválido. Valores permitidos: {list(Vuelo.Estado.values)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        vuelo.estado = nuevo_estado
        vuelo.save()
        return Response({'status': f'Estado actualizado a {vuelo.get_estado_display()}'})

    # GET /api/vuelos/{id}/asientos/
    # Devuelve layout con ocupación para ese vuelo
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def asientos(self, request, pk=None):
        vuelo = self.get_object()
        asientos = Asiento.objects.filter(avion=vuelo.avion).order_by('fila', 'columna')

        ocupados = set(
            Reserva.objects.filter(
                vuelo=vuelo,
                estado=Reserva.Estado.CONFIRMADA,
                asiento__isnull=False
            ).values_list('asiento_id', flat=True)
        )

        data = []
        for a in asientos:
            data.append({
                'id': a.id,
                'fila': a.fila,
                'columna': a.columna,
                'ocupado': a.id in ocupados
            })
        return Response(data)

    # GET /api/vuelos/{id}/verificar_asiento/?asiento_id=123
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def verificar_asiento(self, request, pk=None):
        vuelo = self.get_object()
        asiento_id = request.query_params.get('asiento_id')

        if not asiento_id:
            return Response({'error': 'Debe enviar asiento_id'}, status=400)

        try:
            asiento = Asiento.objects.get(id=asiento_id, avion=vuelo.avion)
        except Asiento.DoesNotExist:
            return Response({'disponible': False, 'error': 'Asiento inexistente para este vuelo'}, status=404)

        ocupado = Reserva.objects.filter(
            vuelo=vuelo,
            asiento=asiento,
            estado=Reserva.Estado.CONFIRMADA
        ).exists()

        return Response({'disponible': not ocupado})


# =====================================================
# 3. PASAJEROS (Registrar + consultar + reservas)
# =====================================================

class PasajeroViewSet(viewsets.ModelViewSet):
    """
    - POST /api/pasajeros/ → registrar pasajero (público)
    - GET /api/pasajeros/{id}/ → ver info (solo admin o el mismo user)
    - GET /api/pasajeros/{id}/reservas/ → reservas de un pasajero (admin)
    - GET /api/pasajeros/mis-reservas/ → reservas del usuario logueado
    """
    queryset = Usuario.objects.all()
    serializer_class = PasajeroSerializer

    # GET /api/pasajeros/me/
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    # GET /api/pasajeros/{id}/reservas/
    @action(detail=True, methods=['get'])
    def reservas(self, request, pk=None):
        pasajero = self.get_object()
        reservas = Reserva.objects.filter(pasajero=pasajero)
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data)

    # GET /api/pasajeros/mis-reservas/
    @action(detail=False, methods=['get'])
    def mis_reservas(self, request):
        reservas = Reserva.objects.filter(pasajero=request.user)
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data)


# =====================================================
# 4. RESERVAS (Crear, seleccionar asiento, cambiar estado)
# =====================================================

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        if self.action in ['cambiar_estado']:
            return [permissions.IsAdminUser()]
        if self.action in ['seleccionar_asiento']:
            return [permissions.IsAuthenticated()]
        # listar/detalle: admin
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        """
        Crear una reserva para un pasajero en un vuelo.
        El pasajero es el usuario autenticado.
        """
        vuelo = serializer.validated_data.get('vuelo')

        if vuelo.estado != Vuelo.Estado.PROGRAMADO or vuelo.fecha_salida < timezone.now():
            raise serializers.ValidationError("No se puede reservar en este vuelo.")

        serializer.save(
            pasajero=self.request.user,
            estado=Reserva.Estado.PENDIENTE
        )

    # POST /api/reservas/{id}/seleccionar_asiento/
    @action(detail=True, methods=['post'])
    def seleccionar_asiento(self, request, pk=None):
        reserva = self.get_object()

        # Solo el dueño o admin
        if not (request.user.is_staff or request.user == reserva.pasajero):
            return Response({'error': 'No autorizado'}, status=403)

        asiento_id = request.data.get('asiento_id')
        if not asiento_id:
            return Response({'error': 'Debe enviar asiento_id'}, status=400)

        try:
            asiento = Asiento.objects.get(id=asiento_id, avion=reserva.vuelo.avion)
        except Asiento.DoesNotExist:
            return Response({'error': 'Asiento inválido para este vuelo'}, status=404)

        # Verificar disponibilidad
        ocupado = Reserva.objects.filter(
            vuelo=reserva.vuelo,
            asiento=asiento,
            estado=Reserva.Estado.CONFIRMADA
        ).exclude(id=reserva.id).exists()

        if ocupado:
            return Response({'error': 'Asiento ya ocupado'}, status=400)

        reserva.asiento = asiento
        reserva.estado = Reserva.Estado.CONFIRMADA
        reserva.save()

        return Response({'status': 'Asiento asignado y reserva confirmada'})

    # PATCH /api/reservas/{id}/cambiar_estado/
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        reserva = self.get_object()
        nuevo_estado = request.data.get('estado')

        if nuevo_estado not in Reserva.Estado.values:
            return Response(
                {'error': f"Estado inválido. Valores: {list(Reserva.Estado.values)}"},
                status=400
            )

        reserva.estado = nuevo_estado
        reserva.save()
        return Response({'status': f'Estado actualizado a {reserva.get_estado_display()}'})


# =====================================================
# 5. BOLETOS (Generar desde reserva + consultar por código)
# =====================================================

import uuid

class BoletoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    - GET /api/boletos/{codigo}/ → consultar boleto
    - POST /api/boletos/generar/ → generar boleto desde reserva confirmada
    """
    queryset = Boleto.objects.all()
    serializer_class = BoletoSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'codigo'  # /api/boletos/ABC123/

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Boleto.objects.all()
        return Boleto.objects.filter(reserva__pasajero=user)

    # POST /api/boletos/generar/
    @action(detail=False, methods=['post'])
    def generar(self, request):
        reserva_id = request.data.get('reserva_id')
        if not reserva_id:
            return Response({'error': 'Debe enviar reserva_id'}, status=400)

        try:
            reserva = Reserva.objects.get(id=reserva_id, pasajero=request.user)
        except Reserva.DoesNotExist:
            return Response({'error': 'Reserva no encontrada'}, status=404)

        if reserva.estado != Reserva.Estado.CONFIRMADA:
            return Response({'error': 'La reserva debe estar CONFIRMADA'}, status=400)

        # Si ya existe boleto, lo devolvemos
        existente = Boleto.objects.filter(reserva=reserva).first()
        if existente:
            serializer = self.get_serializer(existente)
            return Response(serializer.data)

        # Crear boleto (ajustá campos según tu modelo Boleto)
        codigo = uuid.uuid4().hex[:10].upper()
        boleto = Boleto.objects.create(
            reserva=reserva,
            codigo=codigo,
        )
        serializer = self.get_serializer(boleto)
        return Response(serializer.data, status=201)


# =====================================================
# 6. REPORTES (Pasajeros por vuelo / Reservas activas)
# =====================================================

class PasajerosPorVueloReport(APIView):
    permission_classes = [permissions.IsAdminUser]

    # GET /api/reportes/pasajeros-por-vuelo/?vuelo_id=1
    def get(self, request):
        vuelo_id = request.query_params.get('vuelo_id')
        if not vuelo_id:
            return Response({'error': 'Debe enviar vuelo_id'}, status=400)

        try:
            vuelo = Vuelo.objects.get(id=vuelo_id)
        except Vuelo.DoesNotExist:
            return Response({'error': 'Vuelo no encontrado'}, status=404)

        reservas = Reserva.objects.filter(
            vuelo=vuelo,
            estado=Reserva.Estado.CONFIRMADA
        )
        pasajeros = [r.pasajero for r in reservas]
        serializer = PasajeroSerializer(pasajeros, many=True)
        return Response(serializer.data)


class ReservasActivasPorPasajeroReport(APIView):
    permission_classes = [permissions.IsAdminUser]

    # GET /api/reportes/reservas-activas/?pasajero_id=1
    def get(self, request):
        pasajero_id = request.query_params.get('pasajero_id')
        if not pasajero_id:
            return Response({'error': 'Debe enviar pasajero_id'}, status=400)

        try:
            pasajero = Usuario.objects.get(id=pasajero_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Pasajero no encontrado'}, status=404)

        reservas = Reserva.objects.filter(
            pasajero=pasajero,
            estado=Reserva.Estado.CONFIRMADA
        )
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data)
