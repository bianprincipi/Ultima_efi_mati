from io import BytesIO

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .forms import LoginForm, RegistroForm, ReservaForm, VueloAdminForm
from .models import Boleto, Asiento, Reserva, Vuelo


# =================================================================
# 0. BOLETO EN PDF
# =================================================================

@login_required(login_url=reverse_lazy("login"))
def boleto_pdf_view(request, reserva_pk):
    """
    Genera y descarga el boleto en PDF para una reserva confirmada del usuario.
    """
    reserva = get_object_or_404(
        Reserva,
        pk=reserva_pk,
        pasajero=request.user,
        estado=Reserva.Estado.CONFIRMADA,
    )

    boleto, _ = Boleto.objects.get_or_create(reserva=reserva)

    # Crear PDF en memoria
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Encabezado
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, height - 80, "AeroEfi - Boleto de Vuelo")

    # Datos del pasajero
    p.setFont("Helvetica", 12)
    y = height - 130
    nombre = reserva.pasajero.get_full_name() or reserva.pasajero.username
    p.drawString(80, y, f"Pasajero: {nombre}")
    y -= 20
    documento = getattr(reserva.pasajero, "documento", "N/A")
    p.drawString(80, y, f"Documento: {documento}")
    y -= 40

    # Datos del vuelo
    vuelo = reserva.vuelo
    p.setFont("Helvetica-Bold", 13)
    p.drawString(80, y, "Detalles del Vuelo:")
    p.setFont("Helvetica", 12)
    y -= 20
    p.drawString(100, y, f"Código de Vuelo: {vuelo.codigo_vuelo}")
    y -= 20
    p.drawString(100, y, f"Origen: {vuelo.origen}")
    y -= 20
    p.drawString(100, y, f"Destino: {vuelo.destino}")
    y -= 20
    p.drawString(100, y, f"Salida: {vuelo.fecha_salida.strftime('%d/%m/%Y %H:%M')}")
    y -= 20
    p.drawString(100, y, f"Llegada: {vuelo.fecha_llegada.strftime('%d/%m/%Y %H:%M')}")

    # Asiento
    y -= 40
    p.setFont("Helvetica-Bold", 13)
    p.drawString(80, y, "Asiento:")
    p.setFont("Helvetica", 12)
    y -= 20
    asiento_txt = (
        f"{reserva.asiento.fila}{reserva.asiento.columna}"
        if reserva.asiento
        else "SIN ASIENTO"
    )
    p.drawString(100, y, f"Asiento: {asiento_txt}")

    # Código de boleto
    y -= 40
    p.setFont("Helvetica-Bold", 13)
    p.drawString(80, y, "Código de Boleto:")
    p.setFont("Helvetica", 16)
    y -= 30
    p.drawString(100, y, boleto.codigo_barra)

    # Footer
    p.setFont("Helvetica", 8)
    p.drawString(
        80,
        60,
        "Presentar este boleto en el aeropuerto junto con tu documento.",
    )
    p.drawString(
        80,
        45,
        "Generado automáticamente por el sistema de gestión de aerolínea.",
    )

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="boleto_{boleto.codigo_barra}.pdf"'
    return response


# =================================================================
# PERFIL
# =================================================================

@login_required(login_url=reverse_lazy("login"))
def perfil_view(request):
    """
    Perfil del usuario pasajero/admin.
    """
    return render(request, "gestion/perfil.html", {"user": request.user})


# =================================================================
# 1. MIXIN DE PERMISOS (ADMIN)
# =================================================================

class AdminRequiredMixin(UserPassesTestMixin):
    """
    Bloquea el acceso a la vista si el usuario no es Admin.
    Usa la propiedad .is_admin del modelo Usuario.
    """

    login_url = reverse_lazy("login")

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and getattr(self.request.user, "is_admin", False)
        )


# =================================================================
# 2. VISTAS PÚBLICAS / AUTENTICACIÓN
# =================================================================

class ListaVuelosView(ListView):
    """
    Listado público de vuelos disponibles.
    """
    model = Vuelo
    template_name = "gestion/vuelos_list.html"
    context_object_name = "vuelos"

    def get_queryset(self):
        # Si querés filtrar solo futuros / programados, podés ajustar acá.
        return Vuelo.objects.all().order_by("fecha_salida")


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.first_name or user.username}!")

            if getattr(user, "is_admin", False):
                return redirect("vuelos_admin_list")
            return redirect("vuelos_disponibles")

        messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()

    return render(request, "gestion/login.html", {"form": form})


def registro_view(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                "¡Cuenta creada con éxito! Bienvenido a bordo.",
            )
            return redirect("vuelos_disponibles")

        messages.error(request, "Hubo un error en el registro. Revise los datos.")
    else:
        form = RegistroForm()

    return render(request, "gestion/registro.html", {"form": form})


# =================================================================
# 3. VISTAS DE GESTIÓN HTML (CRUD ADMIN)
# =================================================================

class VueloAdminListView(AdminRequiredMixin, ListView):
    model = Vuelo
    template_name = "gestion/vuelo_admin_list.html"
    context_object_name = "vuelos"


class VueloCreateView(AdminRequiredMixin, CreateView):
    model = Vuelo
    form_class = VueloAdminForm
    template_name = "gestion/vuelo_form.html"
    success_url = reverse_lazy("vuelos_admin_list")


class VueloUpdateView(AdminRequiredMixin, UpdateView):
    model = Vuelo
    form_class = VueloAdminForm
    template_name = "gestion/vuelo_form.html"
    success_url = reverse_lazy("vuelos_admin_list")


class VueloDeleteView(AdminRequiredMixin, DeleteView):
    model = Vuelo
    template_name = "gestion/vuelo_confirm_delete.html"
    success_url = reverse_lazy("vuelos_admin_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(
                request,
                f"El vuelo {self.object.codigo_vuelo} fue eliminado correctamente.",
            )
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar este vuelo porque tiene reservas o asientos asociados. "
                "Primero cancela o elimina esas reservas antes de borrar el vuelo.",
            )
        return redirect(self.success_url)


# =================================================================
# 4. VISTAS DE RESERVA Y PASAJERO
# =================================================================

@login_required(login_url=reverse_lazy("login"))
def detalle_vuelo_view(request, pk):
    """
    Muestra el detalle del vuelo y opciones de reserva.
    """
    vuelo = get_object_or_404(Vuelo, pk=pk)
    return render(request, "gestion/vuelo_detalle.html", {"vuelo": vuelo})


@login_required(login_url=reverse_lazy("login"))
def crear_reserva_view(request, vuelo_pk):
    """
    Crea una reserva en estado PENDIENTE (sin asiento) y redirige al selector.
    """
    vuelo = get_object_or_404(Vuelo, pk=vuelo_pk)

    # Si ya tiene una reserva activa/pending para este vuelo
    reserva_existente = (
        Reserva.objects.filter(
            pasajero=request.user,
            vuelo=vuelo,
            estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.CONFIRMADA],
        ).first()
    )

    if reserva_existente:
        messages.warning(
            request,
            "Ya tienes una reserva activa o pendiente para este vuelo.",
        )
        return redirect("reserva_detalle", pk=reserva_existente.pk)

    if request.method == "POST":
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.vuelo = vuelo
            reserva.pasajero = request.user
            reserva.estado = Reserva.Estado.PENDIENTE
            reserva.save()
            messages.success(
                request,
                "Reserva creada con éxito. Ahora selecciona tu asiento.",
            )
            return redirect("seleccionar_asiento", reserva_pk=reserva.pk)
    else:
        form = ReservaForm()

    return render(
        request,
        "gestion/reserva_form.html",
        {"form": form, "vuelo": vuelo},
    )


@login_required(login_url=reverse_lazy("login"))
def seleccionar_asiento_view(request, reserva_pk):
    """
    Muestra el mapa de asientos y permite al pasajero seleccionar uno.
    Genera el boleto automáticamente cuando se confirma el asiento.
    """
    reserva = get_object_or_404(
        Reserva,
        pk=reserva_pk,
        pasajero=request.user,
    )
    vuelo = reserva.vuelo

    # Asientos del vuelo
    asientos_vuelo = Asiento.objects.filter(vuelo=vuelo).order_by("fila", "columna")

    if not asientos_vuelo.exists():
        messages.error(
            request,
            "Este vuelo no tiene asientos configurados. Contacta al administrador.",
        )
        return redirect("reserva_detalle", pk=reserva.pk)

    # Asientos ocupados por otras reservas P o C
    asientos_ocupados_ids = (
        Reserva.objects.filter(
            vuelo=vuelo,
            estado__in=[Reserva.Estado.CONFIRMADA, Reserva.Estado.PENDIENTE],
        )
        .exclude(pk=reserva.pk)
        .values_list("asiento_id", flat=True)
    )

    # Construir layout para el template
    filas_dict = {}
    columnas_set = set()

    for asiento in asientos_vuelo:
        if asiento.fila not in filas_dict:
            filas_dict[asiento.fila] = {"fila": asiento.fila, "celdas": []}

        ocupado = asiento.id in asientos_ocupados_ids
        filas_dict[asiento.fila]["celdas"].append(
            {
                "asiento": asiento,
                "ocupado": ocupado,
            }
        )
        columnas_set.add(asiento.columna)

    layout = [filas_dict[f] for f in sorted(filas_dict.keys())]
    columnas = sorted(list(columnas_set))

    if request.method == "POST":
        asiento_id = request.POST.get("asiento_id")

        if not asiento_id:
            messages.error(request, "Debes seleccionar un asiento.")
            return redirect("seleccionar_asiento", reserva_pk=reserva.pk)

        asiento_seleccionado = get_object_or_404(
            Asiento,
            id=asiento_id,
            vuelo=vuelo,
        )

        # Verificar disponibilidad final
        if asiento_seleccionado.id in asientos_ocupados_ids:
            messages.error(
                request,
                "Ese asiento ya fue ocupado. Elegí otro.",
            )
            return redirect("seleccionar_asiento", reserva_pk=reserva.pk)

        with transaction.atomic():
            reserva.asiento = asiento_seleccionado
            reserva.estado = Reserva.Estado.CONFIRMADA
            reserva.save()

            # Crear boleto si no existe
            Boleto.objects.get_or_create(reserva=reserva)

        messages.success(
            request,
            f"Asiento {asiento_seleccionado.fila}{asiento_seleccionado.columna} confirmado. "
            f"Se generó tu boleto.",
        )
        return redirect("reserva_detalle", pk=reserva.pk)

    return render(
        request,
        "gestion/asiento_selector.html",
        {
            "vuelo": vuelo,
            "reserva": reserva,
            "layout": layout,
            "columnas": columnas,
        },
    )


@login_required(login_url=reverse_lazy("login"))
def reserva_detalle_view(request, pk):
    """
    Muestra los detalles de una reserva específica del usuario.
    """
    reserva = get_object_or_404(
        Reserva,
        pk=pk,
        pasajero=request.user,
    )
    vuelo = reserva.vuelo

    return render(
        request,
        "gestion/reserva_detalle.html",
        {
            "reserva": reserva,
            "vuelo": vuelo,
        },
    )
