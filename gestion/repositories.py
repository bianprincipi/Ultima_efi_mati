# gestion/repositories.py

from django.db import transaction
from django.db.models import Q
from .models import Vuelo, Asiento, Reserva, Usuario 
# Nota: Asegúrate de que los modelos tienen definidas las constantes como Vuelo.Estado.PROGRAMADO

# =================================
# 1. REPOSITORIO DE VUELOS
# =================================

class VueloRepository:
    """
    Capa responsable del acceso a datos para la entidad Vuelo.
    """
    @staticmethod
    def listar_todos():
        return Vuelo.objects.all().order_by('fecha_salida')

    @staticmethod
    def listar_disponibles():
        # Filtra por el estado PROGRAMADO (asumiendo que existe)
        return Vuelo.objects.filter(estado=Vuelo.Estado.PROGRAMADO).order_by('fecha_salida')
    
    # ... (Aquí irían otros métodos como get_by_id, crear, actualizar, etc.)


# =================================
# 2. REPOSITORIO DE RESERVAS (CORREGIDO)
# =================================

class ReservaRepository:
    """
    Capa responsable del acceso a datos para la entidad Reserva.
    """

    # 💥 MÉTODOS DE LISTADO FALTANTES 💥
    @staticmethod
    def listar_todas():
        """Obtiene todas las reservas. Usado por el Admin."""
        return Reserva.objects.all()

    @staticmethod
    def listar_por_pasajero(pasajero_id):
        """
        Obtiene las reservas filtradas por el ID del pasajero.
        ¡ESTO SOLUCIONA EL ÚLTIMO 500!
        """
        # Filtramos las reservas donde el campo 'pasajero' es igual al ID proporcionado
        return Reserva.objects.filter(pasajero_id=pasajero_id)

    # ----------------------------------------------------
    # MÉTODOS DE CREACIÓN Y BÚSQUEDA (Los que ya tenías)
    # ----------------------------------------------------

    @staticmethod
    def get_reserva_by_id_and_pasajero(reserva_id, pasajero):
        return Reserva.objects.get(pk=reserva_id, pasajero=pasajero)

    @staticmethod
    def get_vuelo_disponible_by_id(vuelo_id):
        # Asumo que tienes un campo de estado en tu modelo Vuelo
        return Vuelo.objects.get(pk=vuelo_id, estado=Vuelo.Estado.PROGRAMADO) 

    @staticmethod
    def get_asiento_disponible(vuelo, asiento_id):
        return Asiento.objects.get(
            vuelo=vuelo, 
            pk=asiento_id, 
            estado=Asiento.Estado.DISPONIBLE
        )
        
    @staticmethod
    @transaction.atomic
    def crear_reserva_y_actualizar_asiento(vuelo, asiento, pasajero, precio_final, codigo_reserva):
        """Crea la reserva y marca el asiento como ocupado."""
        
        # 1. Crear la Reserva
        reserva = Reserva.objects.create(
            vuelo=vuelo,
            asiento=asiento,
            pasajero=pasajero,
            precio_final=precio_final,
            codigo_reserva=codigo_reserva,
            # fecha_reserva=timezone.now() # O si se autogenera en el modelo, no es necesario
        )
        
        # 2. Marcar el Asiento como Ocupado
        asiento.estado = Asiento.Estado.OCUPADO
        asiento.save()
        
        return reserva