✈️ AeroLineaEFI – Sistema de Gestión de Aerolínea

DSW-2025 - Ingeniería de Software
Proyecto: Sistema de Gestión de Aerolínea (Ultima_efi_mati)

AeroLineaEFI es una aplicación web desarrollada en Django que permite gestionar de forma integral los vuelos, reservas y pasajeros de una aerolínea. El sistema ofrece funcionalidades tanto para usuarios finales como para administradores, incluyendo autenticación, vistas específicas y generación de boletos en PDF.

🌟 Características principales
🔐 Autenticación de usuarios

Registro e inicio de sesión.

Perfil personal (vista perfil.html).

Distinción entre usuarios normales y administradores (staff).

🛫 Gestión de vuelos

Listado de vuelos disponibles.

Creación, edición y eliminación desde la sección administrativa (vuelo_admin.html).

Visualización completa del vuelo (origen, destino, fecha/hora, capacidad, etc.).

🎫 Gestión de reservas

Creación de reservas asociadas a usuarios y vuelos.

Consulta y visualización de reservas.

Cancelación o modificación según reglas de negocio.

👥 Gestión de pasajeros

Manejo de datos personales de los pasajeros.

Listado y detalles relevantes (nombre, documento, contacto, etc.).

💺 Manejo de asientos

Asignación de asientos por vuelo.

Control de disponibilidad.

Restricciones para evitar duplicaciones.

📄 Generación de boletos en PDF

Creación de boletos a partir de reservas confirmadas.

Plantilla boleto_pdf.html.

Generación con librerías como xhtml2pdf.

📊 Panel de resumen

Vista resumen.html con estadísticas generales del sistema.

Útil para administración interna.

🖥️ Interfaz moderna y reutilizable

Uso de base.html como plantilla principal.

Templates ordenados en gestion/templates/gestion/.

🧱 Arquitectura del Proyecto
Ultima_efi_mati/
├─ aerolinea/
│  ├─ settings.py      # Configuración principal
│  ├─ urls.py          # Rutas globales
│  ├─ wsgi.py / asgi.py
│
├─ gestion/
│  ├─ models.py        # Modelos principales
│  ├─ views.py         # Lógica del sistema
│  ├─ forms.py         # Formularios
│  ├─ repositories.py  # Acceso a datos
│  ├─ migrations/      # Migraciones de base de datos
│  └─ templates/gestion/
│      ├─ base.html
│      ├─ perfil.html
│      ├─ vuelo_admin.html
│      ├─ boleto_pdf.html
│      └─ resumen.html
│
├─ manage.py
└─ venv/ / env/        # Entornos virtuales (no versionar)


⚙️ Instalación y uso rápido

1️⃣ Clonar el repositorio
git clone https://github.com/bianprincipi/Ultima_efi_mati.git
cd Ultima_efi_mati

2️⃣ Crear y activar entorno virtual
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
# .\venv\Scripts\activate

3️⃣ Instalar dependencias
pip install -r requirements.txt

4️⃣ Aplicar migraciones
python manage.py migrate

5️⃣ Crear superusuario
python manage.py createsuperuser

6️⃣ Ejecutar el servidor
python manage.py runserver


Aplicación: http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

🔐 Credenciales del Sistema (Modo Demo)

🛡️ Administrador

Usuario: Aerolínea

Contraseña: itec1020B

👤 Pasajero

Usuario: Pasajero

Contraseña: Pass123

💻 Comandos útiles
python manage.py createsuperuser
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
python manage.py shell

🧑‍💻 Autores

Antonella Caceres

Bianca Principi

⚖️ Licencia

Proyecto bajo licencia MIT. Consulte el archivo LICENSE para más información.

