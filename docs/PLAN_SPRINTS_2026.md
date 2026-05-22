# PLAN DE DESARROLLO EN SPRINTS: CONGRESO DE LOGÍSTICA Y TRANSPORTE 2026
## Enfoque Integrado: DevSecOps, Seguridad de Infraestructura y UI/UX Premium de Alto Impacto
### [Rama de Trabajo Activa: `feature/plan-sprints-2026`]

Este documento define la hoja de ruta estratégica estructurada en **Sprints** para llevar la plataforma del congreso a su máximo nivel de robustez, confiabilidad, seguridad y excelencia visual. 

Este plan ha sido refinado incorporando el **análisis y contraste directo con la base de código real** de la aplicación y las aclaraciones operativas del equipo técnico.

---

```mermaid
gantt
    title Cronograma de Sprints - Congreso UNAB 2026 (Refinado)
    dateFormat  YYYY-MM-DD
    section Backend & DevSecOps
    Sprint 1: Seguridad & Backups Drive   :active, s1, 2026-05-25, 10d
    Sprint 2: Contenedores con Control CI/CD: s2, after s1, 10d
    section Frontend & UI/UX Premium
    Sprint 3: UX y Animaciones (Marca Lila) : s3, after s2, 12d
    section Integración & Escalabilidad
    Sprint 4: Optimización & Errores 404/500: s4, after s3, 10d
```

---

## 🏃 SPRINT 1: CIMIENTOS DE SEGURIDAD Y RESPALDOS (DEVSECOPS)
**Duración Sugerida:** 10 días  
**Objetivo del Sprint:** Mitigar de inmediato las vulnerabilidades críticas del servidor universitario, resolver la seguridad de cookies y automatizar respaldos hacia Google Drive en formato de planilla de cálculo de lectura sencilla.

### 📋 Requerimientos y Tareas Técnicas

#### 1. Reparación de Seguridad en Cookies (Django)
* **Archivo a modificar:** [settings.py](file:///c:/Users/User/Desktop/Congreso-UNAB-main/backend/core/settings.py)
* **Ajuste Técnico:** Asegurar que las variables de seguridad `CSRF_COOKIE_SECURE = True` y `SESSION_COOKIE_SECURE = True` se ejecuten estrictamente bajo `if not DEBUG:` al final del archivo para evitar anulaciones accidentales de desarrollo.
* **Impacto:** Protege el robo de credenciales en redes universitarias abiertas.

#### 2. Auditoría de Conectividad Saliente (Outbound Traffic)
* **Objetivo:** Verificar si las políticas del Firewall de la universidad permiten la conectividad saliente del servidor físico hacia las APIs externas indispensables.
* **Acciones:** Ejecutar pruebas directas de comunicación:
  * Probar salida a Telegram: `curl -I https://api.telegram.org`
  * Probar salida a Google APIs: `curl -I https://www.googleapis.com`
  * De registrarse bloqueos de red, gestionar con el departamento de TI académica la habilitación de excepciones.

#### 3. Backups Offsite: Sincronización Automática a Google Sheets
* **Archivo a crear:** `backend/scripts/sync_to_sheets.py`
* **Implementación:**
  * Desarrollar una integración en Python utilizando la API de Google Sheets y una cuenta de servicio de Google Cloud (`gspread`).
  * Generar un volcado semanal de las tablas críticas de base de datos (Asistentes, Disertantes, Representantes) directamente a una **Planilla de Google Sheets** en Drive.
  * Mantener esta planilla actualizada automáticamente como copia de seguridad interactiva y de fácil lectura para el equipo organizador del congreso sin depender de dumps SQL crudos.
  * Mantener complementariamente un cron diario nocturno para backups de PostgreSQL tradicionales.

#### 4. Pre-generación Estática del Código QR Único
* **Archivo a optimizar:** [qr_views.py](file:///c:/Users/User/Desktop/Congreso-UNAB-main/backend/api/qr_views.py)
* **Ajuste Técnico:** Dado que el QR de asistencia es estático y sirve como control de ingreso único redirigiendo a `/verificar-dni`, desviaremos su procesamiento fuera de la lógica dinámica de Django.
  * Generar los QRs definitivos en formato PNG.
  * Guardarlos de forma física en el directorio de estáticos (`/var/www/congreso/static/qrs/`).
  * Nginx servirá estas imágenes directamente desde el disco, reduciendo a cero el consumo de CPU de Pillow y base64 durante las peticiones masivas del día del evento.

### 📦 Entregables del Sprint 1
- [ ] Cookies Django configuradas de forma estrictamente segura.
- [ ] Reporte de auditoría de red de salida (Firewall) aprobado.
- [ ] Script de sincronización semanal automática hacia Google Sheets activo.
- [ ] Códigos QR estáticos guardados físicamente y servidos por Nginx.

---

## 🏃 SPRINT 2: TRANSICIÓN A CONTENEDORES CON CANAL DE CONTROL EN CI/CD
**Duración Sugerida:** 10 días  
**Objetivo del Sprint:** Contenedorizar la plataforma para aislar componentes, manteniendo al **GitHub Self-Hosted Runner** como consola de administración remota de comandos de emergencia mediante automatizaciones.

### 📋 Requerimientos y Tareas Técnicas

#### 1. Arquitectura Containerizada Aislada
* **Archivos a crear:** `Dockerfile` (backend) y `docker-compose.prod.yml` (raíz).
* **Especificaciones:**
  * Dockerfile *multi-stage* basado en `python:3.11-slim` ejecutándose bajo usuario no-root.
  * Compose estructurado con redes bridge aisladas. La base de datos corre sin puertos expuestos al host físico para máxima seguridad de red.

#### 2. Mapeo de Control Remoto de Emergencia (GitHub Actions)
* **Consideración Operativa:** El administrador no posee SSH directo al servidor y utiliza comandos con sudo desde el pipeline de GitHub como consola administrativa ("consola ciega").
* **Solución Técnica:** Crear workflows interactivos en GitHub Actions (`.github/workflows/admin_commands.yml`) que expongan un disparador manual (`workflow_dispatch`), permitiendo ejecutar tareas de control de forma segura dentro de los contenedores Docker:
  * **Acción de Migración:** `/venv/bin/python manage.py migrate`
  * **Acción de Recolección:** `/venv/bin/python manage.py collectstatic`
  * **Acción de Logs:** `docker compose logs -n 150 congreso-backend`
  * **Acción de Shell:** Ejecutar comandos de control autorizados dentro de la red del contenedor.
  * **Reinicio en Caliente:** Re-desplegar de emergencia un contenedor particular si la app experimenta bloqueos.
  * De esta forma, el administrador mantiene el 100% de su capacidad de intervención remota y solución de errores a través de GitHub, pero operando de manera estructurada y segura bajo Docker.

### 📦 Entregables del Sprint 2
- [ ] Ficheros Dockerfile y Docker-Compose probados.
- [ ] Workflow administrativo de control remoto interactivo configurado en GitHub Actions.
- [ ] Pipeline de despliegue actualizado a contenedores en caliente.

---

## 🏃 SPRINT 3: UX INMERSIVA Y ANIMACIONES (PRESERVANDO PALETA LILA)
**Duración Sugerida:** 12 días  
**Objetivo del Sprint:** Elevar visualmente la visión de la aplicación incorporando micro-interacciones, efectos dinámicos de hover y transiciones fluidas, respetando de manera estricta la paleta lila/violeta característica de la marca.

### 📋 Requerimientos y Tareas Técnicas

#### 1. Consolidación de la Identidad Visual Existente
* **Ajuste de Diseño:** Se prohíbe cambiar o alterar la paleta cromática existente del congreso.
* **Valores de Marca a Mantener:**
  * Lila Oscuro / Fondo base: `#2d1854` (o `var(--congress-blue-dark)`).
  * Lila Claro / Acentos: `var(--congress-cyan)` (`270 60% 65%`).
  * Degradados y banners representativos de la marca.
* **Acciones de Refinamiento UX:**
  * Reemplazar las fuentes del navegador por tipografías modernas suavizadas (ej. **Plus Jakarta Sans** para cuerpo, **Outfit** o similar para títulos grandes).
  * Aplicar efectos de desenfoque de fondo translúcido (*glassmorphism*) integrados armónicamente con los fondos lilas actuales para ganar elegancia y modernidad.

#### 2. Transiciones Fluidas y Animaciones Orgánicas (Framer Motion / CSS3)
* **Hero Interactivo:** Animación de entrada suave donde los componentes emergen en cascada escalonada con desvanecimientos progresivos.
* **Patrocinadores Dinámicos:**
  * Carrusel infinito con movimiento continuo suave acelerado por hardware (`translate3d` para evitar saltos en pantallas de alta tasa de refresco).
  * Detener progresivamente el movimiento al pasar el cursor encima (`pause-on-hover` con desaceleración orgánica) y reanudar de la misma forma.
* **Efectos Hover Tridimensionales:**
  * Aplicar efectos de rotación interactiva en perspectiva (*tilt effect*) en tarjetas de stands y disertantes, proyectando una iluminación translúcida lila que persigue al cursor del usuario.

#### 3. Formularios con Feedback Visual Táctil
* **Confirmación de Asistencia / Validación DNI:**
  * Animación de enfoque progresiva del campo.
  * Transición de alerta elástica ante errores (leve temblor de vibración horizontal en lila/rojo suave).
  * Efectos de carga suaves dentro de los botones de envío, transformándose en un check SVG animado tras la validación exitosa.

### 📦 Entregables del Sprint 3
- [ ] Tipografías estilizadas integradas en el cliente React.
- [ ] Transiciones de entrada de componentes fluidas implementadas en la homepage.
- [ ] Carrusel de auspiciantes con pause-on-hover suavizado por hardware.
- [ ] Formularios de registro con micro-interacciones interactivas operando bajo el tema lila actual.

---

## 🏃 SPRINT 4: OPTIMIZACIÓN DE CORREOS, BOLSA DE TRABAJO Y ERRORES PERSONALIZADOS
**Duración Sugerida:** 10 días  
**Objetivo del Sprint:** Corregir latencias y potenciales Timeouts en el envío masivo de correos, optimizar el rendimiento visual de la Bolsa de Trabajo en producción y diseñar páginas de error específicas de alto diseño.

### 📋 Requerimientos y Tareas Técnicas

#### 1. Optimización de la Bolsa de Trabajo (Módulo en Producción)
* **Aclaración del Proyecto:** La funcionalidad de Bolsa de Trabajo ya se encuentra activa en producción.
* **Acciones de Sprint:**
  * **Optimización Visual:** Agregar transiciones fluidas de filtrado y búsqueda de ofertas de empleo auspiciadas por sponsors 2026.
  * **Carga Segura de CVs:** Validar visualmente la carga de archivos PDF grandes con un loader dinámico de barra de progreso y arrastrar-y-soltar (*drag-and-drop*) animado.
  * **Consultas eficientes:** Optimizar las consultas a la base de datos de las candidaturas para garantizar respuestas veloces en el dashboard administrativo.

#### 2. Robustez en Envío de Emails Masivos por Lotes (Gateway Timeout Fix)
* **Archivo a auditar/modificar:** [email.py (función send_broadcast_batch_email)](file:///c:/Users/User/Desktop/Congreso-UNAB-main/backend/api/email.py)
* **Ajuste Técnico:** La función actual efectúa un loteo síncrono correcto de a `25` correos con demoras de `time.sleep(2)` para resguardar la reputación de la cuenta SMTP. No obstante, al correr en el hilo de ejecución principal, bloquea la petición web de Django y produce un código de error de Nginx `504 Gateway Timeout` al enviar boletines a listas medianas/grandes.
* **Solución Propuesta:**
  * Encapsular la lógica de loteo de `send_broadcast_batch_email` en una **tarea asíncrona de segundo plano (Celery)**, o
  * Exponer un comando administrativo de Django (`python manage.py send_bulk_newsletter`) que sea disparado asíncronamente en segundo plano.
  * De esta forma, el panel web del administrador responde "Envío Iniciado" al instante en 0.1 segundos y la carga pesada se procesa en el fondo del servidor universitario de forma paulatina sin colgar la aplicación de producción.

#### 3. Páginas de Error Personalizadas y Específicas
* **Objetivo:** Ofrecer una UX inmersiva y amigable incluso cuando el sistema experimenta fallas o enlaces caídos.
* **Detalle de Implementación:** Crear vistas HTML/React únicas e ilustradas para:
  * **Error 404 (No Encontrado):** Animación en lila de un camión de logística que toma una salida de ruta equivocada o un paquete extraviado en una estantería infinita.
  * **Error 500 (Fallo de Servidor):** Animación de un motor logístico de cintas transportadoras en mantenimiento temporal, con un mensaje claro e integrando un botón directo de recarga simple.

### 📦 Entregables del Sprint 4
- [ ] Bolsa de Trabajo optimizada visualmente y con carga segura de CVs en PDF.
- [ ] Envío masivo de emails encapsulado asíncronamente en segundo plano (solución definitiva al Gateway Timeout 504).
- [ ] Vistas e ilustraciones animadas de error 404 y 500 completadas.
