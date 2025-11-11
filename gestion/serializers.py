# gestion/serializers.py

from rest_framework import serializers
from .models import Vuelo, Avion, Usuario, Asiento, Reserva, Boleto# Importa todos los modelos necesarios

class PasajeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        # ajustá campos según tu modelo de usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class BoletoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boleto
        fields = '__all__'
# =================================================================
# 1. SERIALIZADORES DE MODELOS BÁSICOS
# =================================================================

class AvionSerializer(serializers.ModelSerializer):
    """Serializa la información del modelo Avion."""
    class Meta:
        model = Avion
        fields = '__all__'


class AsientoSerializer(serializers.ModelSerializer):
    """Serializa la información del modelo Asiento."""
    class Meta:
        model = Asiento
        fields = '__all__'


class TripulanteSerializer(serializers.ModelSerializer):
    """Serializador simple para la tripulación/usuarios."""
    class Meta:
        model = Usuario
        # Solo campos no sensibles para la vista pública de tripulación
        fields = ['id', 'username', 'first_name', 'last_name', 'rol']


# =================================================================
# 2. SERIALIZADOR DE VUELO (Relaciones)
# =================================================================

class VueloSerializer(serializers.ModelSerializer):
    """
    Serializa la información del modelo Vuelo, incluyendo relaciones anidadas
    para la lectura y campos de solo escritura para la creación/edición.
    """
    # Campo de solo lectura para mostrar el modelo del avión sin exponer la FK en la lectura
    avion_modelo = serializers.CharField(source='avion.modelo', read_only=True)
    
    # Campo para manejar la FK del avión en la escritura (POST/PUT)
    avion = serializers.PrimaryKeyRelatedField(
        queryset=Avion.objects.all(),
        # Si usas 'avion', DRF lo mapeará directamente al campo FK del modelo.
        write_only=True,
        required=True,
        label="ID del Avión"
    )

    # Serializador anidado para mostrar la tripulación completa en la lectura
    tripulacion_detallada = TripulanteSerializer(source='tripulacion', many=True, read_only=True)
    
    # Campo para manejar la relación Many-to-Many de tripulación en la escritura
    tripulacion = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), 
        many=True, 
        write_only=True,
        required=False,
        label="IDs de la Tripulación"
    )

    class Meta:
        model = Vuelo
        fields = [
            'id', 'codigo_vuelo', 'origen', 'destino', 'fecha_salida', 
            'fecha_llegada', 'estado', 'precio_base', 
            # Lectura
            'avion_modelo', 'tripulacion_detallada',
            # Escritura
            'avion', 'tripulacion'
        ]
        read_only_fields = ['id', 'avion_modelo', 'tripulacion_detallada']


# =================================================================
# 3. SERIALIZADOR DE RESERVA (API de Pasajero)
# =================================================================

class ReservaSerializer(serializers.ModelSerializer):
    """Serializa la información de una reserva específica."""
    
    # Anidamos el asiento y el vuelo para dar más contexto al pasajero
    asiento_info = AsientoSerializer(source='asiento', read_only=True)
    vuelo_info = VueloSerializer(source='vuelo', read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'vuelo', 'pasajero', 'asiento', 'estado', 'fecha_reserva',
            'asiento_info', 'vuelo_info'
        ]
        read_only_fields = ['id', 'pasajero', 'fecha_reserva']
        
    def validate(self, data):
        """Valida que un asiento no esté ocupado."""
        if self.instance is None and 'asiento' in data: # Solo para creación
            asiento_a_reservar = data['asiento']
            vuelo = data.get('vuelo')
            
            if Reserva.objects.filter(vuelo=vuelo, asiento=asiento_a_reservar, estado=Reserva.Estado.CONFIRMADA).exists():
                raise serializers.ValidationError("Este asiento ya está ocupado en el vuelo seleccionado.")
        
        return data
        
        