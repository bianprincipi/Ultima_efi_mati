from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
import random
import string

# =========================
# USUARIO (PASAJERO / ADMIN)
# =========================

class Usuario(AbstractUser):
    documento = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(r'^[0-9]+$', 'Solo se permiten números')]
    )
    telefono = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?[0-9]+$', 'Formato de teléfono inválido')]
    )
    fecha_nacimiento = models.DateField(null=True, blank=True)

    class Rol(models.TextChoices):
        ADMIN = 'AD', 'Administrador'
        PASAJERO = 'PA', 'Pasajero'

    rol = models.CharField(max_length=2, choices=Rol.choices, default=Rol.PASAJERO)

    def __str__(self):
        return f"{self.get_full_name() or self.username} - {self.get_rol_display()}"

    @property
    def is_admin(self):
        return self.rol == self.Rol.ADMIN

    @property
    def is_pasajero(self):
        return self.rol == self.Rol.PASAJERO


# ==========
# AVIÓN
# ==========

class Avion(models.Model):
    modelo = models.CharField(max_length=100)
    capacidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    filas = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    columnas = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    matricula = models.CharField(max_length=10, unique=True)
    fecha_fabricacion = models.DateField(default=timezone.now)
    ultimo_mantenimiento = models.DateField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Aviones"
        ordering = ['modelo']

    def __str__(self):
        return f"{self.modelo} ({self.matricula})"


# ==========
# VUELO
# ==========

class Vuelo(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADO = 'programado', _('Programado')
        DEMORADO = 'demorado', _('Demorado')
        CANCELADO = 'cancelado', _('Cancelado')
        COMPLETADO = 'completado', _('Completado')
        EN_CURSO = 'en_curso', _('En Curso')

    avion = models.ForeignKey(Avion, on_delete=models.PROTECT, related_name='vuelos')
    codigo_vuelo = models.CharField(max_length=10, unique=True)
    origen = models.CharField(max_length=100, db_index=True)
    destino = models.CharField(max_length=100, db_index=True)
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    duracion = models.DurationField(null=True, blank=True)

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PROGRAMADO
    )

    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    # Tripulación: solo usuarios con rol ADMIN
    tripulacion = models.ManyToManyField(
        Usuario,
        limit_choices_to={'rol': Usuario.Rol.ADMIN},
        blank=True,
        related_name='vuelos_asignados'
    )

    class Meta:
        ordering = ['fecha_salida']
        indexes = [
            models.Index(fields=['origen', 'destino']),
            models.Index(fields=['fecha_salida']),
        ]

    def __str__(self):
        return f"{self.codigo_vuelo}: {self.origen} → {self.destino}"

    def clean(self):
        if self.fecha_salida and self.fecha_llegada:
            if self.fecha_llegada <= self.fecha_salida:
                raise ValidationError("La fecha de llegada debe ser posterior a la fecha de salida.")
        super().clean()

    @property
    def cancelado(self):
        return self.estado == self.Estado.CANCELADO


# ==========
# ASIENTO
# ==========

class Asiento(models.Model):
    class Tipo(models.TextChoices):
        ECONOMY = 'economy', _('Economy')
        PREMIUM = 'premium', _('Premium')
        BUSINESS = 'business', _('Business')
        FIRST = 'first', _('First Class')

    class Ocupacion(models.TextChoices):
        DISPONIBLE = 'disponible', _('Disponible')
        RESERVADO = 'reservado', _('Reservado')
        OCUPADO = 'ocupado', _('Ocupado')
        MANTENIMIENTO = 'mantenimiento', _('En Mantenimiento')

    avion = models.ForeignKey(Avion, on_delete=models.CASCADE, related_name='asientos')
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE, related_name='asientos')
    numero = models.CharField(max_length=10)
    fila = models.PositiveIntegerField()
    columna = models.CharField(max_length=5)

    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.ECONOMY
    )

    estado = models.CharField(
        max_length=20,
        choices=Ocupacion.choices,
        default=Ocupacion.DISPONIBLE
    )

    precio_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ['vuelo', 'numero']
        ordering = ['fila', 'columna']

    def __str__(self):
        return f"Asiento {self.numero} - {self.vuelo.codigo_vuelo}"


# ==========
# RESERVA
# ==========

class Reserva(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'P', 'Pendiente'
        CONFIRMADA = 'C', 'Confirmada'
        CANCELADA = 'X', 'Cancelada'

    vuelo = models.ForeignKey(Vuelo, on_delete=models.PROTECT, related_name='reservas')
    pasajero = models.ForeignKey('Usuario', on_delete=models.PROTECT, related_name='reservas')
    asiento = models.ForeignKey(
        'Asiento',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='reservas'
    )
    estado = models.CharField(
        max_length=1,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reserva {self.id} - {self.pasajero} - {self.vuelo}"
    @property
    def precio_final(self):
        base = self.vuelo.precio_base if self.vuelo and self.vuelo.precio_base else 0
        extra = self.asiento.precio_extra if self.asiento else 0
        return base + extra

# ==========
# BOLETO
# ==========

class Boleto(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = 'activo', _('Activo')
        USADO = 'usado', _('Usado')
        ANULADO = 'anulado', _('Anulado')

    reserva = models.OneToOneField(Reserva, on_delete=models.PROTECT, related_name='boleto')
    codigo_barra = models.CharField(max_length=50, unique=True, editable=False)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    fecha_checkin = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)
    puerta_embarque = models.CharField(max_length=5, blank=True)

    class Meta:
        ordering = ['-fecha_emision']

    def __str__(self):
        return f"Boleto {self.codigo_barra} ({self.get_estado_display()})"

    def save(self, *args, **kwargs):
        if not self.codigo_barra:
            self.codigo_barra = self.generar_codigo_barra()
        super().save(*args, **kwargs)

    def generar_codigo_barra(self):
        # Usa datos existentes y algo random
        base = f"{self.reserva.vuelo.codigo_vuelo}-{self.reserva.pasajero.id}-{self.reserva.id}"
        return f"B-{base}-{uuid.uuid4().hex[:4].upper()}"

    def marcar_como_usado(self):
        self.estado = self.Estado.USADO
        self.fecha_checkin = timezone.now()
        self.save()

    def anular(self):
        self.estado = self.Estado.ANULADO
        self.save()
