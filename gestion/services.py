# gestion/services.py

import random, string
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied
# Asegúrate de que los Repositories y Models están importados correctamente
from .repositories import VueloRepository, ReservaRepository 
from .models import Asiento, Vuelo, Usuario, Reserva # Importa modelos necesarios


# --------------------------------
# 1. SERVICIO DE VUELOS (Asegurando la existencia para el ImportError)
# --------------------------------

class VueloService: 
    """
    Contiene la lógica de negocio para la gestión de Vuelos.
    """

    @staticmethod
    def listar_todos():
        return VueloRepository.listar_todos()
    
    @staticmethod
    def listar_disponibles():
        return VueloRepository.listar_disponibles()

    @staticmethod
    def crear_vuelo(data):
        return VueloRepository.crear(data)

    @staticmethod
    def cancelar_vuelo(vuelo_id):
        try:
            vuelo = VueloRepository.get_by_id(vuelo_id)
            # Lógica de negocio (notificaciones, etc.)
            return VueloRepository.cancelar(vuelo)
        except Vuelo.DoesNotExist:
            raise ValidationError(f"Vuelo con ID {vuelo_id} no encontrado.")

# --------------------------------
# 2. SERVICIO DE RESERVAS (CORREGIDO para el 500)
# --------------------------------

class ReservaService:
    """
    Contiene la lógica de negocio crítica para la gestión de Reservas.
    """
    
    # 💥 MÉTODOS DE LISTADO (Añadidos para solucionar el 500 anterior) 💥
    @staticmethod
    def listar_todas():
        """Lista todas las reservas. Usado por los Administradores."""
        return ReservaRepository.listar_todas()

    @staticmethod
    def listar_por_pasajero(pasajero_id):
        """
        Lista las reservas asociadas a un pasajero específico.
        """
        # Delegamos en el Repositorio para la lógica de filtrado
        return ReservaRepository.listar_por_pasajero(pasajero_id)
    
    @staticmethod
    def generar_codigo_reserva():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    @staticmethod
    def calcular_precio(vuelo, asiento):
        # Lógica de negocio: precio_base + recargo por clase de asiento
        recargo = 0
        # Asumiendo que Asiento.Clase es una enumeración o constante
        # ... (Lógica de precio, como la tenías) ...
        return vuelo.precio_base + recargo


    @staticmethod
    def crear_reserva(vuelo_id, asiento_id, usuario):
        # Lógica de creación de reserva
        if not usuario.rol == Usuario.Rol.PASAJERO:
            raise PermissionDenied("Solo los pasajeros pueden realizar reservas.")
            
        try:
            vuelo = ReservaRepository.get_vuelo_disponible_by_id(vuelo_id)
            asiento = ReservaRepository.get_asiento_disponible(vuelo, asiento_id)

            precio_final = ReservaService.calcular_precio(vuelo, asiento)
            codigo = ReservaService.generar_codigo_reserva()

            reserva = ReservaRepository.crear_reserva_y_actualizar_asiento(
                vuelo=vuelo,
                asiento=asiento,
                pasajero=usuario,
                precio_final=precio_final,
                codigo_reserva=codigo
            )
            return reserva
            
        except Vuelo.DoesNotExist:
            raise ValidationError(f"Vuelo con ID {vuelo_id} no encontrado o no disponible.")
        except Asiento.DoesNotExist:
            raise ValidationError(f"Asiento con ID {asiento_id} no existe o ya fue reservado.")