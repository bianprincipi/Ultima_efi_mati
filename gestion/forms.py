# gestion/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

from .models import Vuelo, Reserva, Asiento, Avion
# Importa todos los modelos necesarios para los formularios
Usuario = get_user_model() 

# ==========================================================
# 1. FORMULARIOS DE AUTENTICACIÓN
# ==========================================================

# Necesario para views.login_view
class LoginForm(AuthenticationForm):
    """Formulario base para la autenticación de usuarios."""
    # Django ya maneja los campos 'username' y 'password'. 
    # Puedes añadir estilos o personalizar mensajes si lo deseas.
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))

# Necesario para views.registro_view
class RegistroForm(UserCreationForm):
    """
    Formulario para la creación de nuevos usuarios (Pasajeros).
    Asume que el campo 'rol' se establecerá a PASAJERO por defecto en el modelo o en la vista.
    """
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}))

    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Excluimos el campo 'rol' si todos los registros son Pasajeros. 
        # Si no, el usuario tendría que seleccionar su rol.
        fields = ('username', 'email', 'first_name', 'last_name',)
        # Asegúrate de que 'username' y 'password' se manejen correctamente por UserCreationForm

# ==========================================================
# 2. FORMULARIOS DE GESTIÓN (ADMIN)
# ==========================================================

# Necesario para VueloCreateView y VueloUpdateView
class VueloAdminForm(forms.ModelForm):
    """
    Formulario completo para que el Administrador cree y edite vuelos.
    """
    # Usamos un queryset específico para mostrar solo usuarios que pueden ser tripulación (si aplica)
    tripulacion = forms.ModelMultipleChoiceField(
        queryset=Usuario.objects.filter(rol=Usuario.Rol.ADMIN), # Ejemplo: solo Admins como tripulación
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Vuelo
        fields = [
            'codigo_vuelo', 'origen', 'destino', 'fecha_salida', 
            'fecha_llegada', 'precio_base', 'avion', 'estado', 'tripulacion'
        ]
        widgets = {
            # Widgets para un mejor manejo de fecha y hora
            'fecha_salida': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'fecha_llegada': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'codigo_vuelo': forms.TextInput(attrs={'class': 'form-control'}),
            'origen': forms.TextInput(attrs={'class': 'form-control'}),
            'destino': forms.TextInput(attrs={'class': 'form-control'}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control'}),
            'avion': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

# ==========================================================
# 3. FORMULARIOS DE RESERVA (PASAJERO)
# ==========================================================

# Necesario para views.crear_reserva_view
class ReservaForm(forms.ModelForm):
    """
    Formulario para la reserva inicial, preguntando la cantidad de asientos.
    """
    # Campo extra que no está en el modelo, solo se usa para el formulario
    cantidad_pasajeros = forms.IntegerField(
        min_value=1, 
        max_value=9, 
        initial=1,
        label='Número de Pasajeros (Máx. 9)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 9})
    )

    class Meta:
        model = Reserva
        # Solo necesitamos este campo para el formulario inicial.
        # Los campos 'vuelo', 'pasajero', 'asiento', 'estado' se manejan en la vista.
        fields = [] 
        
    def clean_cantidad_pasajeros(self):
        """Validación simple para la cantidad de pasajeros."""
        cantidad = self.cleaned_data.get('cantidad_pasajeros')
        if cantidad > 9:
            raise forms.ValidationError("No puedes reservar para más de 9 personas a la vez.")
        return cantidad