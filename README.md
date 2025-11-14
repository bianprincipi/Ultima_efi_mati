DSW-2025 - Ingeniería de Software
Proyecto: Sistema de Gestión de Aerolínea (Ultima_efi_mati)

AeroLineaEFI – Sistema de gestión de vuelos, reservas y pasajeros ✈️
AeroLineaEFI es una aplicación web desarrollada en Django que permite gestionar de forma integral los vuelos, reservas y pasajeros de una aerolínea. El sistema ofrece funcionalidades tanto para usuarios finales (que realizan reservas) como para administradores (que gestionan vuelos, asientos y reportes).

Incluye interfaz web, manejo de autenticación, vistas específicas para administración y generación de boletos en PDF.

🌟 Características principales
🔐 Autenticación de usuarios   - Registro e inicio de sesión.   - Perfil de usuario con datos personales (perfil.html).   - Diferenciación entre usuarios normales y usuarios administradores (staff).

🛫 Gestión de vuelos   - Listado de vuelos disponibles.   - Creación, edición y eliminación de vuelos desde la sección administrativa (vuelo_admin.html).   - Visualización de información clave de cada vuelo (origen, destino, fecha/hora, capacidad, etc.).

🎫 Gestión de reservas   - Creación de reservas asociadas a un vuelo y a un usuario/pasajero.   - Consulta y visualización de reservas existentes.   - Cancelación o actualización del estado de las reservas (según reglas de negocio).

👥 Gestión de pasajeros   - Manejo de datos de pasajeros asociados a las reservas.   - Listados y detalle de la información relevante (nombre, documento, contacto, etc.).

💺 Manejo de asientos   - Asociación de asientos a cada vuelo.   - Control de disponibilidad de asientos.   - Restricciones para evitar duplicados o solapamiento de reservas (definidas a nivel de modelos y migraciones).

📄 Boletos en PDF   - Generación de un boleto a partir de una reserva confirmada.   - Uso de una plantilla específica (boleto_pdf.html) y conversión a PDF mediante librerías como xhtml2pdf / similares.   - Descarga o visualización del boleto para el usuario.

📊 Panel de control / Resumen   - Vista de resumen (resumen.html) con información agregada del sistema (vuelos, reservas, etc.).   - Facilita la gestión interna de la aerolínea simulada.

🖥️ Interfaz moderna y reutilizable   - Uso de plantilla base (base.html) para unificar estilos.   - Estructura de templates ordenada dentro de gestion/templates/gestion/.

🧱 Arquitectura del proyecto
Estructura general del repositorio:

Bash

Ultima_efi_mati/
├─ aerolinea/
│  ├─ __init__.py
│  ├─ settings.py        # Configuración principal del proyecto Django
│  ├─ urls.py            # Ruteo global del proyecto
│  ├─ wsgi.py / asgi.py  # Punto de entrada para el servidor
│
├─ gestion/
│  ├─ __init__.py
│  ├─ models.py          # Modelos: Vuelo, Reserva, Asiento, Usuario extendido, etc.
│  ├─ views.py           # Lógica de vistas para vuelos, reservas, perfil, boletos, etc.
│  ├─ forms.py           # Formularios para creación/edición de entidades
│  ├─ repositories.py    # Capa de acceso a datos / consultas específicas
│  ├─ migrations/        # Historial de cambios de base de datos
│  └─ templates/
│     └─ gestion/
│        ├─ base.html
│        ├─ perfil.html
│        ├─ vuelo_admin.html
│        ├─ boleto_pdf.html
│        └─ resumen.html
│
├─ manage.py             # Script de administración de Django
├─ env/                  # Entorno virtual (no recomendado versionar)
└─ venv/                 # Entorno virtual (no recomendado versionar)

⚙️ Instalación y uso rápido
1️⃣ Clonar el repositorio

Bash
git clone https://github.com/bianprincipi/Ultima_efi_mati.git
cd Ultima_efi_mati
2️⃣ Crear y activar un entorno virtual

Aunque el proyecto puede tener carpetas env/ o venv/ versionadas, se recomienda crear un nuevo entorno virtual limpio y evitar que dichas carpetas sean versionadas (usando .gitignore).

Bash
# Crear entorno virtual
python -m venv venv
# Activar en Linux / Mac
source venv/bin/activate
# Activar en Windows (Cmd o PowerShell)
# .\venv\Scripts\activate
3️⃣ Instalar dependencias

Bash

pip install -r requirements.txt
4️⃣ Aplicar migraciones y preparar base de datos

Bash

python manage.py migrate
5️⃣ Crear superusuario (Administrador):

Bash

python manage.py createsuperuser
6️⃣ Levantar el servidor local

Bash

python manage.py runserver
Aplicación web: http://127.0.0.1:8000/

Panel admin Django: http://127.0.0.1:8000/admin/

🔐 Credenciales del Sistema
🛡️ Rol Administrador

Usuario: Aerolínea
Contraseña: itec1020B

👤 Rol Pasajero

Usuario: Pasajero
Contraseña: Pass123

💻 Comandos útiles
Bash

python manage.py createsuperuser   # Crear usuario administrador
python manage.py makemigrations    # Detectar cambios en modelos y crear migraciones
python manage.py migrate           # Aplicar migraciones a la base de datos
python manage.py runserver         # Levantar servidor local
python manage.py shell             # Consola interactiva con contextos del proyecto

🧑‍💻 Autores
Este proyecto fue desarrollado por:
Antonella Caceres - Bianca Principi
⚖️ Licencia
Este proyecto está bajo la licencia MIT. Consulte el archivo LICENSE para más detalle

⚖️ Licencia
Este proyecto está bajo la licencia MIT. Consulte el archivo LICENSE para más detalles.

