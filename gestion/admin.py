# gestion/admin.py

from django.contrib import admin
from .models import Usuario, Avion, Vuelo, Asiento, Reserva, Boleto

# ---------- USUARIO ----------
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "rol", "is_staff")
    list_filter = ("rol", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email")


# ---------- ASIENTO INLINE (dentro de Vuelo) ----------
class AsientoInline(admin.TabularInline):
    model = Asiento
    extra = 5  # filas vacías para cargar asientos rápido
    fields = ("numero", "fila", "columna", "tipo", "estado", "precio_extra")
    # 'vuelo' y 'avion' se setean automáticamente, no los mostramos:
    can_delete = True

    def save_new_instance(self, form, commit=True):
        """
        (Solo para Django <5; en 5 podés manejar via formset)
        No la usamos acá, vamos con override en VueloAdmin.save_formset.
        """
        instance = form.save(commit=False)
        return instance


# ---------- VUELO ----------
@admin.register(Vuelo)
class VueloAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_vuelo",
        "origen",
        "destino",
        "fecha_salida",
        "fecha_llegada",
        "precio_base",
        "estado",
        "avion",
    )
    list_filter = ("estado", "origen", "destino", "avion")
    search_fields = ("codigo_vuelo", "origen", "destino")
    inlines = [AsientoInline]

    def save_formset(self, request, form, formset, change):
        """
        Cuando guardás los asientos inline, completamos vuelo y avión.
        """
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, Asiento):
                # Vincular al vuelo actual
                obj.vuelo = form.instance
                # Asegurarnos que el avión coincida con el del vuelo
                obj.avion = form.instance.avion
            obj.save()
        # Borrar los marcados para eliminar
        for obj in formset.deleted_objects:
            obj.delete()


# ---------- AVION ----------
@admin.register(Avion)
class AvionAdmin(admin.ModelAdmin):
    list_display = ("modelo", "matricula", "capacidad", "filas", "columnas")
    search_fields = ("modelo", "matricula")


# ---------- RESERVA ----------
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'vuelo', 'pasajero', 'estado', 'fecha_creacion', 'fecha_modificacion')
    list_filter = ('estado', 'vuelo')
    search_fields = ('pasajero__username', 'vuelo__codigo_vuelo')


# ---------- BOLETO ----------
@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_barra",
        "reserva",
        "estado",
        "fecha_emision",
        "fecha_checkin",
    )
    list_filter = ("estado",)
    search_fields = ("codigo_barra", "reserva__pasajero__username")
