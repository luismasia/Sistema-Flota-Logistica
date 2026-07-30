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

## ⚙️ Instalación y Ejecución Local

Siga estos pasos para correr el proyecto en tu entorno local:

1. **Clonar el repositorio:**
   
   git clone [https://github.com/luismasia/Sistema-Flota-Logistica.git](https://github.com/luismasia/Sistema-Flota-Logistica.git)
   cd Sistema-Flota-Logistica

2. **Crear y activar un entorno virtual:**
   En Windows:
   python -m venv venv
   venv\Scripts\activate

   En macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate

3. **Instalar las dependencias:**
   pip install -r requirements.txt

4. **Aplicar las migraciones a la base de datos:**
   python manage.py migrate

5. **Crear un superusuario (opcional, para acceder al panel de admin):**
   python manage.py createsuperuser

6. **Ejecutar el servidor de desarrollo:**
   python manage.py runserver

## 💻 Autor

**Luis Masia**

<a href="https://linkedin.com/in/luismasia" target="_blank"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
<a href="mailto:lnicolasmasia@gmail.com"><img alt="Gmail" src="https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white" /></a>
