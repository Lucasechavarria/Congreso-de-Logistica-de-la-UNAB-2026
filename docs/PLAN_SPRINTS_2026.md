# PLAN DE DESARROLLO EN SPRINTS: CONGRESO DE LOGÍSTICA Y TRANSPORTE 2026
## Enfoque Integrado: DevSecOps, Seguridad de Infraestructura y UI/UX Premium de Alto Impacto

Este documento define la hoja de ruta estratégica estructurada en **Sprints** para llevar la plataforma del congreso a su máximo nivel de robustez, confiabilidad, seguridad y excelencia visual. 

La planificación equilibra la **seguridad de la infraestructura universitaria (on-premise)** con la directiva fundamental de **escalar en funcionalidad y UI/UX**, incorporando un diseño inmersivo, animado y extremadamente refinado.

---

```mermaid
gantt
    title Cronograma de Sprints - Congreso UNAB 2026
    dateFormat  YYYY-MM-DD
    section Backend & DevSecOps
    Sprint 1: Seguridad & Backups       :active, s1, 2026-05-25, 10d
    Sprint 2: Contenedores (Docker)     : s2, after s1, 10d
    section Frontend & UI/UX Premium
    Sprint 3: UI/UX & Animaciones       : s3, after s2, 12d
    section Integración & Escalabilidad
    Sprint 4: Funcionalidades & QA      : s4, after s3, 10d
```

---

## 🏃 SPRINT 1: CIMIENTOS DE SEGURIDAD Y DESPLIEGUE (DEVSECOPS)
**Duración Sugerida:** 10 días  
**Objetivo del Sprint:** Mitigar de inmediato las vulnerabilidades críticas del servidor universitario on-premise detectadas en la auditoría, garantizando la confidencialidad de la información y la resiliencia ante pérdidas catastróficas.

### 📋 Requerimientos y Tareas Técnicas

#### 1. Reparación Inmediata de Seguridad en Cookies (Django)
* **Archivo a modificar:** [settings.py](file:///c:/Users/User/Desktop/Congreso-UNAB-main/backend/core/settings.py)
* **Acción:** Corregir la anulación del token CSRF. Asegurar que las variables `CSRF_COOKIE_SECURE = True` y `SESSION_COOKIE_SECURE = True` se ejecuten estrictamente bajo `if not DEBUG:`.
* **Impacto:** Evita el robo de tokens de sesión y CSRF sobre conexiones no encriptadas en la red de la universidad.

#### 2. Implementación de Rate Limiting (Nginx)
* **Archivo a modificar/crear:** `/etc/nginx/nginx.conf` (en producción).
* **Acción:**
  * Declarar zonas de límite de tasa en el bloque HTTP (`limit_req_zone`).
  * Aplicar restricciones robustas en el endpoint de inscripciones masivas (`/api/inscripciones/`) a un máximo de **1 req/s por IP**, tolerando ráfagas controladas.
  * Proteger el endpoint de generación de certificados y QRs (`/api/qr/`) para neutralizar escaneos abusivos o ataques de denegación de servicio (DoS).

#### 3. Automatización de Copias de Seguridad Off-Site (Costo-Cero)
* **Archivo a crear:** [backend/scripts/backups_offsite.sh](file:///c:/Users/User/Desktop/Congreso-UNAB-main/backend/scripts/backups_offsite.sh)
* **Detalle de Implementación:**
  * Instalación de **Rclone** en el servidor host.
  * Conexión a un almacenamiento en la nube gratuito (Mega 20 GB o Google Drive 15 GB).
  * Programación de un dump automatizado de PostgreSQL con compresión **Zstandard (zstd)** por su baja huella de procesamiento.
  * Encriptación simétrica **AES256** mediante `gpg` antes de la subida para proteger los datos personales de alumnos y ponentes.
  * Programación periódica en `cron` para ejecutarse cada madrugada a las 02:00 AM con limpieza automática local y remota de archivos de más de 14 días.

#### 4. Notificaciones Proactivas de Fallos (Telegram Integration)
* **Archivo a crear:** [scripts/alert_checker.sh](file:///c:/Users/User/Desktop/Congreso-UNAB-main/scripts/alert_checker.sh)
* **Acción:**
  * Script Bash ultraligero que parsea los últimos logs de errores en `/var/log/nginx/error.log` y fallos del servicio systemd.
  * Si se registran errores críticos de tipo 5XX de forma continua, dispara una alerta en tiempo real a través de la API gratuita de Bots de Telegram hacia el chat del equipo técnico.
  * Configuración en cron para ejecutarse cada 5 minutos.

### 📦 Entregables del Sprint 1
- [ ] Directivas de cookies Django seguras en producción.
- [ ] Configuración de Nginx con limitación de tasa activa en endpoints clave.
- [ ] Script de backups off-site encriptado y programado en cron.
- [ ] Sistema de alerta temprana por Telegram operando con un consumo menor a 15MB de RAM.

---

## 🏃 SPRINT 2: TRANSICIÓN A CONTENEDORES E INFRAESTRUCTURA IAC
**Duración Sugerida:** 10 días  
**Objetivo del Sprint:** Aislar completamente los componentes del sistema para erradicar el riesgo de intrusiones transversales y garantizar la reproducibilidad absoluta de la aplicación en el servidor universitario.

### 📋 Requerimientos y Tareas Técnicas

#### 1. Creación del Entorno Dockerizado
* **Archivos a crear:** `Dockerfile` (raíz del backend) y `docker-compose.prod.yml` (raíz del proyecto).
* **Especificaciones del Dockerfile:**
  * Configuración *multi-stage* utilizando `python:3.11-slim` para reducir drásticamente el peso de la imagen y los tiempos de compilación.
  * Creación y ejecución de la aplicación bajo un usuario sin privilegios (`django-user`), garantizando que si el contenedor es comprometido, el atacante no obtenga acceso root en el host.
* **Especificaciones del Docker-Compose:**
  * Declaración de tres redes bridge virtuales completamente aisladas:
    * `frontend-net`: Nginx proxy <--> Frontend React SPA.
    * `backend-net`: Nginx proxy <--> Backend Django.
    * `db-net`: Backend Django <--> PostgreSQL.
  * **Aislamiento Estricto:** La base de datos PostgreSQL *no* expone puertos al host, eliminando cualquier posibilidad de conexión externa directa.
  * Límites estrictos de memoria RAM y CPU por contenedor en el bloque `deploy.resources.limits` para evitar la congelación de la VM universitaria ante fugas de recursos.

#### 2. Adaptación del Pipeline de CI/CD (GitHub Actions)
* **Archivo a modificar:** [.github/workflows/deploy.yml](file:///c:/Users/User/Desktop/Congreso-UNAB-main/.github/workflows/deploy.yml)
* **Acción:**
  * Sustituir el proceso actual de `rsync` y reinicio manual de servicios locales por el despliegue nativo de contenedores (`docker compose up -d --build`).
  * Eliminar comandos peligrosos como `pkill -9 gunicorn` y comandos de sudo sin contraseña.
  * Integrar la inyección segura de secretos del servidor mediante GitHub Secrets y variables de Docker Compose.

#### 3. Automatización de SSL con Certbot Containerizado
* **Acción:** Configurar un contenedor auxiliar o volumen compartido que gestione de forma autónoma la renovación de los certificados SSL de Let's Encrypt para `www.congresologistica.unab.edu.ar`, refrescando la configuración de Nginx automáticamente sin intervención manual.

### 📦 Entregables del Sprint 2
- [ ] Dockerfile de Django optimizado y seguro (Non-Root).
- [ ] docker-compose.prod.yml operando con 3 redes aisladas.
- [ ] Pipeline de despliegue automatizado basado en contenedores Docker.
- [ ] Certificados de seguridad SSL configurados para renovación automática a costo cero.

---

## 🏃 SPRINT 3: EXPERIENCIA DE USUARIO PREMIUM Y ANIMACIONES DE ALTO IMPACTO
**Duración Sugerida:** 12 días  
**Objetivo del Sprint:** Transformar por completo la estética visual de la plataforma. Diseñar una interfaz interactiva y "viva" que genere un impacto inmediato en el usuario a través de micro-interacciones, transiciones fluidas y una paleta moderna, dejando atrás las fuentes y estructuras por defecto.

### 📋 Requerimientos y Tareas Técnicas

#### 1. Establecer el Sistema de Diseño y Tokens Visuales
* **Archivo a modificar/crear:** [client/global.css](file:///c:/Users/User/Desktop/Congreso-UNAB-main/client/global.css) e `index.html` (para Google Fonts).
* **Tipografía de Alta Gama:**
  * Incorporar la tipografía premium **Outfit** o **Cabinet Grotesk** para títulos de secciones, aportando una estética robusta y geométrica muy alineada con el sector de Logística y Transporte.
  * Usar la tipografía **Inter** para el cuerpo de texto, priorizando la legibilidad en pantallas y dispositivos móviles.
* **Paleta HSL Curada (Efecto Cyber-Logistics / Dark Mode Moderno):**
  * Color base de fondo: HSL muy oscuro, sofisticado y profundo (`#0b0f19` o `hsl(222, 47%, 7%)`).
  * Color de acento primario: Azul cobalto brillante y eléctrico (`hsl(217, 91%, 60%)`).
  * Color de acento secundario: Cian fosforescente o esmeralda tecnológico para botones de llamada a la acción y estados activos (`hsl(180, 100%, 50%)`).
  * Integración de **Glassmorphism** (fondos translúcidos difusos mediante `backdrop-filter: blur(12px)` con bordes ultrafinos semi-transparentes de `rgba(255,255,255,0.08)`).

#### 2. Desarrollo de Animaciones e Interacciones Premium (React / Framer Motion o CSS3)
* **Hero Section Dinámico (Primer Impacto):**
  * Animación de entrada escalonada (*staggered animations*) donde el título, el subtítulo y los botones principales se deslizan suavemente con un leve efecto de desvanecimiento hacia arriba.
  * Fondo dinámico sutil con un gradiente animado radial que se desplaza lentamente, emulando flujo e interconexión logística.
* **Carrusel de Sponsors Acreditados (Edición 2026):**
  * Movimiento infinito ultra suave sin saltos visuales mediante keyframes CSS optimizados por hardware (`translate3d`).
  * Efecto de desaceleración progresiva e interactiva cuando el cursor pasa por encima (*pause on hover* con transición elástica).
* **Tarjetas de Disertantes con Efecto de Profundidad Tridimensional:**
  * Efecto de hover interactivo en tarjetas: pequeña rotación en perspectiva (*tilt effect*) combinada con un gradiente de borde luminoso que sigue el movimiento del cursor.
  * Desplazamiento sutil hacia arriba (`translateY(-8px)`) y sombra proyectada difusa de color neón del color de acento.

#### 3. Formularios Dinámicos con Feedback Visual Orgánico
* **Validación Dinámica de DNI:**
  * Input interactivo: El borde del campo se ilumina suavemente con una transición HSL al enfocarse.
  * Mensajes de error con animación de entrada elástica (*bounce effect*) y vibración horizontal leve ante datos incorrectos.
* **Micro-animaciones en Botones de Envío:**
  * Al hacer clic, el botón cambia suavemente a un estado de carga (un spinner minimalista fluido dentro del botón).
  * Al completarse con éxito la inscripción, el botón se transforma con un efecto de escala y muestra un check dinámico animado dibujado con SVG.

### 📦 Entregables del Sprint 3
- [ ] Sistema de diseño implementado en CSS global con tipografías y paletas modernas HSL.
- [ ] Hero Section con animaciones de entrada fluidas y fondo interactivo.
- [ ] Carrusel de patrocinadores dinámico e interactivo optimizado.
- [ ] Tarjetas de disertantes con efectos 3D interactivos al pasar el cursor.
- [ ] Formularios de inscripción modernos con transiciones de feedback en tiempo real.

---

## 🏃 SPRINT 4: ESCALABILIDAD, OPTIMIZACIÓN E INTEGRACIÓN DE FUNCIONALIDADES
**Duración Sugerida:** 10 días  
**Objetivo del Sprint:** Optimizar el rendimiento de la API backend para tolerar altos volúmenes de peticiones y expandir la plataforma con herramientas interactivas que aumenten la utilidad del congreso.

### 📋 Requerimientos y Tareas Técnicas

#### 1. Caché e Ineficiencia de CPU en la API de QRs
* **Archivo a modificar:** [qr_views.py](file:///c:/Users/User/Desktop/Congreso-UNAB-main/backend/api/qr_views.py)
* **Acción:**
  * Modificar la vista de generación de QRs estáticos para que verifique si los archivos de imagen ya están generados en el directorio `/static/qrs/`.
  * Si ya existen, servirlos directamente como archivos estáticos Nginx, desviando la carga de trabajo de Pillow y la codificación base64 fuera de Python.
  * Si no existen, generarlos una sola vez durante el inicio de la aplicación o las migraciones y persistirlos.
* **Impacto:** Reduce el consumo de CPU del backend en un **98%** durante picos de concurrencia.

#### 2. Portal de Bolsa de Trabajo Integrado (Nueva Funcionalidad)
* **Acción:**
  * Crear un módulo en el backend (`bolsa_trabajo`) para registrar ofertas de empleo de las empresas auspiciantes de la edición 2026.
  * Diseñar una interfaz en el cliente React atractiva y moderna con filtros interactivos por área logística y tipo de contratación.
  * Permitir que los alumnos acreditados carguen su Currículum Vitae (PDF) directamente a través del formulario de manera segura.

#### 3. Gestión Asíncrona de Tareas de Emailing (Celery / Fallback Seguro)
* **Acción:**
  * Configurar Celery en segundo plano con Redis como broker para enviar certificados en PDF y correos de confirmación sin demorar la respuesta HTTP del usuario.
  * Mantener el mecanismo de contingencia síncrono estructurado en `settings.py` (`CELERY_TASK_ALWAYS_EAGER`) si el broker Redis experimenta caídas, garantizando que el correo se envíe de todos modos.

#### 4. Experiencia de Errores Inmersiva (Páginas 404 / 500)
* **Acción:** Diseñar páginas de error personalizadas y hermosas en el frontend. Usar ilustraciones modernas con animaciones divertidas relacionadas con la logística (por ejemplo, un paquete perdido flotando en el espacio) para mantener la identidad visual del congreso incluso ante fallos del sistema.

### 📦 Entregables del Sprint 4
- [ ] API de generación de QRs optimizada con servido estático de disco.
- [ ] Portal de Bolsa de Trabajo interactivo integrado para sponsors y alumnos.
- [ ] Gestión asíncrona de envío de correos y PDFs activa y tolerante a fallos.
- [ ] Páginas de error 404 y 500 personalizadas y con alto diseño visual.

---

## 🛠️ TECNOLOGÍAS NECESARIAS E INSUMOS PARA EL TRABAJO
Para asegurar el éxito del plan en sprints, el equipo requerirá los siguientes insumos técnicos y de software (todos de categoría gratuita y open-source):

1. **Docker & Docker Compose (v2.x+):** Para el aislamiento y despliegue del entorno en el servidor universitario Debian/Ubuntu.
2. **Rclone:** Cliente CLI ultraligero configurado con un conector para Mega o Google Drive gratuito.
3. **Pillow & Qrcode (Python):** Librerías existentes en el proyecto que se optimizarán mediante la estrategia de caché.
4. **Framer Motion (React) o Animaciones CSS3 puras:** Para las animaciones fluidas del frontend en [client/](file:///c:/Users/User/Desktop/Congreso-UNAB-main/client/).
5. **Google Fonts (Outfit & Inter):** Fuentes tipográficas de carga asíncrona desde CDN pública o integradas localmente para evitar dependencias de internet.
6. **Telegram Bot Token & Chat ID:** Cuenta de bot de Telegram gratuita creada a través de BotFather para la observabilidad proactiva del sistema.
