# Sistema de Gestión de Flota Logística 🚛

Plataforma web Full Stack desarrollada para la administración integral de vehículos, choferes, sedes y viajes. El sistema automatiza procesos logísticos en tiempo real, asegura la integridad de los datos y optimiza la experiencia del usuario final.

## 🚀 Funcionalidades Principales

*   **Gestión Integral (CRUD):** Administración completa de choferes, vehículos, sedes operativas y viajes siguiendo el patrón arquitectónico MTV (Model-Template-View) mediante Vistas Basadas en Clases (CBV).
*   **Asignación Inteligente (Máquina de Estados):** Lógica de negocio automatizada que controla la disponibilidad de recursos. Los vehículos y choferes cambian su estado de disponibilidad en tiempo real según el progreso y la finalización de los viajes.
*   **Formularios Dinámicos (AJAX):** Implementación de la API Fetch (JavaScript) para la actualización asincrónica de formularios dependientes (ej: filtrado de choferes disponibles según la ciudad de origen), evitando recargas de página y mejorando la UX.
*   **Validaciones Cruzadas:** Seguridad robusta en el backend para evitar inconsistencias lógicas (ej: prevenir la asignación de un vehículo en mantenimiento o un chofer ya ocupado en las mismas fechas).
*   **Base de Datos Optimizada:** Uso avanzado del ORM de Django (`annotate`, `Q objects`, `Case/When`, custom properties) para reducir la carga del servidor y agilizar el filtrado de datos relacionales.

## 🛠️ Tecnologías Utilizadas

*   **Backend:** Python 3, Django
*   **Frontend:** HTML5, CSS3, Bootstrap 5, Vanilla JavaScript (API Fetch)
*   **Base de Datos:** SQLite (Django ORM)
*   **Control de Versiones:** Git, GitHub

## 🌐 Demo en Vivo

<a href="https://sistema-flota-logistica.onrender.com" target="_blank"><img src="https://img.shields.io/badge/Ver_Demo-00C7B7?style=for-the-badge&logo=render&logoColor=white" alt="Demo en vivo"></a>

> ⚠️ **Nota:** al estar alojado en el plan gratuito de Render, el servicio puede tardar unos segundos en cargar en la primera visita tras un período de inactividad.

Los datos de la demo se resetean automáticamente cada 10 minutos a su estado inicial, para que la experiencia se mantenga limpia y consistente para todos los visitantes.

## ⚙️ Instalación y Ejecución Local
Siga estos pasos para correr el proyecto en su entorno local:
1. **Clonar el repositorio:**\
   git clone https://github.com/luismasia/Sistema-Flota-Logistica.git \
   cd Sistema-Flota-Logistica
2. **Crear y activar un entorno virtual:**\
   En Windows:\
   python -m venv venv\
   venv\Scripts\activate
   
   En macOS/Linux:\
   python3 -m venv venv\
   source venv/bin/activate
4. **Instalar las dependencias:**\
   pip install -r requirements.txt
5. **Configurar las variables de entorno:**\
   Cree un archivo `.env` en la raíz del proyecto con el siguiente contenido:\
   SECRET_KEY=tu-clave-secreta-aqui\
   DEBUG=True\
   ALLOWED_HOSTS=127.0.0.1,localhost
   
   Puede generar una SECRET_KEY con:\
   python -c "import secrets; print(secrets.token_urlsafe(50))"
7. **Aplicar las migraciones a la base de datos:**\
   python manage.py migrate
8. **Crear un superusuario (opcional, para acceder al panel de admin):**\
   python manage.py createsuperuser
9. **Ejecutar el servidor de desarrollo:**\
   python manage.py runserver

## 💻 Autor

**Luis Masia**

<a href="https://linkedin.com/in/luismasia" target="_blank"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
<a href="mailto:lnicolasmasia@gmail.com"><img alt="Gmail" src="https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white" /></a>
