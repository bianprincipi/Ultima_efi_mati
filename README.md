# ✈️ Aurora Airlines – Sistema de Gestión de Reservas

Proyecto desarrollado con **Django 5.2.4** que permite gestionar vuelos, reservas, asientos y boletos de pasajeros, con un panel de administración para el personal de la aerolínea.

---

## 🚀 Características principales

- **Gestión completa de vuelos** (crear, editar, eliminar).
- **Panel administrativo** protegido para usuarios administradores.
- **Registro y autenticación** de usuarios pasajeros.
- **Reserva de vuelos en línea.**
- **Selección de asientos visual.**
- **Generación automática de boletos en PDF.**
- **Perfil de usuario con información personal y foto.**

---

## 🧱 Tecnologías utilizadas

- **Backend:** Django 5.2.4 (Python 3.12)
- **Base de datos:** SQLite (por defecto)
- **Frontend:** HTML5, Bootstrap 5, CSS3
- **PDF Generator:** ReportLab
- **Autenticación:** Sistema de usuarios de Django

---

## ⚙️ Instalación y configuración

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/tuusuario/aerolinea.git
cd aerolinea
```

### 2️⃣ Crear y activar un entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Linux / Mac
venv\Scripts\activate     # En Windows
```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

Si no existe el archivo `requirements.txt`, podés generarlo así:
```bash
pip freeze > requirements.txt
```

### 4️⃣ Ejecutar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Crear un superusuario (para el panel admin)

```bash
python manage.py createsuperuser
```

### 6️⃣ Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

Luego abrí tu navegador en:  
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📂 Estructura del proyecto

```
proyecto-aerolinea/
│
├── aerolinea/                # Configuración principal del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── gestion/                  # App principal
│   ├── admin.py              # Configuración del panel admin
│   ├── models.py             # Modelos: Vuelo, Reserva, Asiento, Boleto, Usuario
│   ├── views.py              # Lógica principal (reservas, PDF, perfil)
│   ├── urls.py               # Rutas específicas de la app
│   ├── forms.py              # Formularios de Django
│   ├── templates/gestion/    # Templates HTML
│   │   ├── base.html
│   │   ├── vuelos_list.html
│   │   ├── vuelo_detalle.html
│   │   ├── reserva_form.html
│   │   ├── asiento_selector.html
│   │   ├── reserva_detalle.html
│   │   ├── perfil.html
│   │   └── login / registro
│   └── static/gestion/       # Archivos estáticos (CSS, JS, imágenes)
│
└── venv/                     # Entorno virtual (no subir a GitHub)
```

---

## ✈️ Flujo de uso

### 👤 Usuario pasajero:
1. Se **registra** o inicia sesión.
2. Visualiza los **vuelos disponibles**.
3. Selecciona un vuelo y **crea una reserva**.
4. Elige su **asiento** desde el mapa visual.
5. Al confirmar el asiento:
   - La reserva pasa a estado **CONFIRMADA**.
   - Se genera automáticamente su **boleto en PDF**.
6. Puede descargarlo desde su panel en **"Detalle de reserva"**.

### 🧑‍💼 Usuario administrador:
1. Accede al panel de Django: `/admin`
2. Gestiona vuelos, asientos, reservas y usuarios.
3. Puede crear vuelos nuevos y configurar sus asientos.

---

## 🪶 Generación de boletos PDF

Los boletos se generan automáticamente con **ReportLab**.  
Incluyen:
- Nombre del pasajero  
- Datos del vuelo (origen, destino, fechas)  
- Número de asiento  
- Código de boleto único (código de barras textual)

El archivo se descarga al confirmar la reserva o desde el botón:
> **“Descargar Boleto en PDF”** en el detalle de la reserva.

---

## 🧑‍💻 Roles y permisos

| Rol | Acceso | Descripción |
|-----|--------|--------------|
| **Admin** | Panel completo, CRUD de vuelos y asientos | Gestiona todo el sistema |
| **Pasajero** | Reserva y visualiza sus vuelos | Solo accede a su propia información |

---

## 🧾 Rutas principales

| Ruta | Descripción |
|------|--------------|
| `/` | Listado de vuelos disponibles |
| `/login/` | Inicio de sesión |
| `/registro/` | Registro de nuevos usuarios |
| `/vuelos/<id>/` | Detalle de un vuelo |
| `/vuelos/<id>/reservar/` | Crear reserva |
| `/reservas/<id>/detalle/` | Ver detalle de la reserva |
| `/reservas/<id>/asientos/` | Selección de asiento |
| `/reservas/<id>/boleto/pdf/` | Descargar boleto en PDF |
| `/perfil/` | Perfil del usuario |
| `/panel/vuelos/` | Panel administrativo de vuelos |

---

## 🧰 Dependencias principales

```text
Django==5.2.4
reportlab==4.2.2
xhtml2pdf==0.2.15
```

Podés agregarlas a `requirements.txt` con:

```bash
pip freeze > requirements.txt
```

---



## 🧑‍💻 Autoras

**Brisa Rocío Ortolan y Tamara Soledad BUstamante**  
Proyecto desarrollado como sistema de gestión para aerolínea – 2025.  
💬 *Desarrollado con Django, amor y café.*

---

## 🪪 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.  
Podés usarlo, modificarlo y distribuirlo libremente.
