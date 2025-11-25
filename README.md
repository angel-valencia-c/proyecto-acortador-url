 URL Tracker MVP

Sistema profesional de acortamiento, redirección y análisis de tráfico web.
Desarrollado en Python utilizando Flask bajo una arquitectura MVC.

Funcionalidades Principales

Núcleo
- Acortador de Enlaces: Generación de identificadores únicos alfanuméricos de 6 caracteres.
- Redirección Inteligente: Manejo de códigos de estado HTTP 302.
- Persistencia: Base de datos relacional SQLite con integridad referencial.

Tracking
El sistema captura métricas detalladas en cada clic antes de redirigir:
- Huella Digital: Dirección IP y User-Agent (Navegador/SO).
- Marketing (UTMs): Captura automática de parámetros `utm_source`, `utm_medium` y `utm_campaign`.
- **Timestamp:** Registro exacto de fecha y hora.

Panel Administrativo (Dashboard)
Interfaz gráfica minimalista (Clean UI) para la gestión:
- Visualización: Tabla de reportes en tiempo real.
- Gestión (CRUD): Edición de URLs destino y Eliminación de enlaces (con borrado en cascada de visitas).
- Exportación: Descarga de reportes completos en formato Excel (.xlsx).

---

Requisitos Previos

- Python 3.x instalado.

Instalación y Ejecución

1. Instalar dependencias:
   Abre tu terminal en la carpeta del proyecto y ejecuta:
   ```bash
   pip install -r requirements.txt