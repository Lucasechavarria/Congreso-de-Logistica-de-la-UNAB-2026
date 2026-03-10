# Sistema de Validación y Actualización de DNI

## Resumen

Sistema completo para validar DNIs de asistentes, limpiar datos incorrectos y permitir que los usuarios actualicen su DNI mediante un enlace único y seguro.

---

## Fases Implementadas

### ✅ Fase 1: Preparación y Limpieza

**Archivos modificados/creados:**
- `backend/api/models.py` - Agregado campo `dni_update_token`
- `backend/fix_dni.py` - Script de limpieza y asignación de tokens

**Ejecución en local (ya hecha):**
```bash
cd backend
source env/bin/activate
python manage.py makemigrations api
python manage.py migrate
python fix_dni.py
```

**Resultados:**
- 343 DNIs corregidos
- 40 asistentes sin DNI válido identificados con token asignado

---

### ✅ Fase 2: Validación Permanente en el Backend

**Archivos modificados:**
- `backend/api/models.py` - Agregado método `clean()` en modelo Asistente
- `backend/api/serializers.py` - Agregado método `validate_dni()` en AsistenteSerializer

**Validaciones implementadas:**
- Solo se aceptan DNIs de exactamente 8 dígitos numéricos
- Se eliminan caracteres no numéricos automáticamente
- Si el DNI tiene 9 dígitos y termina en 0, se elimina el último 0
- Se rechaza cualquier DNI que no cumpla con el formato

**Pruebas ejecutadas:**
```bash
cd backend
python test_dni_validation.py
```
✅ Todas las pruebas pasaron correctamente

---

### ✅ Fase 3: Vista de Actualización de DNI

**Archivos creados:**
- `backend/api/views.py` - Agregada clase `ActualizarDNIView`
- `client/pages/ActualizarDNI.tsx` - Página frontend para actualizar DNI

**Archivos modificados:**
- `backend/api/urls.py` - Agregada ruta `/api/actualizar-dni/`
- `client/App.tsx` - Agregada ruta `/actualizar-dni`

**Funcionalidad:**
- **GET** `/api/actualizar-dni/?token=xxx` - Verifica token y devuelve info del asistente
- **POST** `/api/actualizar-dni/` - Actualiza el DNI y elimina el token

---

### ✅ Fase 4: Acción en el Admin para Envío de Emails

**Archivos creados:**
- `backend/api/templates/email/dni_update.html` - Template HTML del email

**Archivos modificados:**
- `backend/api/admin.py` - Agregada acción `enviar_solicitud_actualizacion_dni`

**Funcionalidad:**
- Desde el admin de Django, seleccionar asistentes sin DNI válido
- Hacer clic en "Enviar solicitud de actualización de DNI"
- Se envía un email con enlace personalizado a cada asistente

---

## Flujo Completo del Sistema

```
1. Admin ejecuta script fix_dni.py
   ↓
2. Se limpian DNIs y se asignan tokens a quienes no tienen DNI válido
   ↓
3. Admin selecciona asistentes sin DNI en el panel de Django
   ↓
4. Admin envía emails masivos con enlace personalizado
   ↓
5. Asistente recibe email con enlace único
   ↓
6. Asistente hace clic en el enlace
   ↓
7. Sistema verifica el token y muestra formulario
   ↓
8. Asistente ingresa su DNI (8 dígitos)
   ↓
9. Sistema valida el DNI (solo 8 dígitos numéricos)
   ↓
10. Si es válido, actualiza el DNI y elimina el token
   ↓
11. Enlace queda inutilizable tras uso exitoso
```

---

## Comandos para Aplicar en Producción

### 1. Subir cambios a GitHub

```bash
git add .
git commit -m "feat: Sistema completo de validación y actualización de DNI"
git push origin main
```

### 2. En la VM - Aplicar migraciones

```bash
ssh usuario@ip_vm
cd /ruta/proyecto
git pull origin main
cd backend
./env/bin/python manage.py makemigrations api
./env/bin/python manage.py migrate
```

### 3. Ejecutar script de limpieza

```bash
./env/bin/python fix_dni.py
```

### 4. Configurar URL del frontend (si no está)

Editar `backend/core/settings.py`:
```python
FRONTEND_URL = 'https://congresologistica.unab.edu.ar'
```

### 5. Reiniciar servicios

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### 6. Compilar frontend

```bash
cd /ruta/proyecto/client
npm run build
```

---

## Uso desde el Admin de Django

1. Acceder al admin: `https://tusitio.com/admin/`
2. Ir a **Asistentes**
3. Filtrar o buscar asistentes sin DNI válido (campo DNI vacío)
4. Seleccionar los asistentes
5. En el menú desplegable de acciones, elegir **"Enviar solicitud de actualización de DNI"**
6. Hacer clic en **"Ir"**
7. Confirmar el envío

---

## Validación en el Frontend

El formulario de actualización de DNI (`/actualizar-dni`) valida:
- Solo acepta 8 dígitos numéricos
- Elimina automáticamente caracteres no numéricos
- Limita el input a 8 caracteres
- Deshabilita el botón si el DNI no tiene 8 dígitos

---

## Archivos Clave

### Backend
- `backend/api/models.py` - Modelo Asistente con validación
- `backend/api/serializers.py` - Validación en API
- `backend/api/views.py` - Vista ActualizarDNIView
- `backend/api/urls.py` - Ruta /actualizar-dni/
- `backend/api/admin.py` - Acción de envío de emails
- `backend/api/templates/email/dni_update.html` - Template del email
- `backend/fix_dni.py` - Script de limpieza

### Frontend
- `client/pages/ActualizarDNI.tsx` - Página de actualización
- `client/App.tsx` - Rutas del frontend

---

## Testing

### Probar validación de modelo y serializer
```bash
cd backend
python test_dni_validation.py
```

### Probar flujo completo en local
1. Ejecutar el script de limpieza
2. Acceder al admin: `http://localhost:8000/admin/`
3. Seleccionar un asistente sin DNI
4. Enviar email de prueba
5. Verificar que el enlace funcione en `http://localhost:5173/actualizar-dni?token=xxx`

---

## Próximas Mejoras (Fase 5 - Opcional)

- Validación de DNI en el formulario de registro de asistentes (frontend)
- Agregar mensaje de error en tiempo real en formularios
- Bloquear envío del formulario si el DNI es inválido

---

## Notas Importantes

- El token es único por asistente y se genera solo para quienes no tienen DNI válido
- El token se elimina tras el uso exitoso del enlace
- Los asistentes con DNI válido no reciben email ni tienen token
- El script `fix_dni.py` usa `.update()` en lugar de `.save()` para evitar problemas con la validación automática durante la limpieza masiva
- La validación es estricta: solo 8 dígitos numéricos, sin excepciones

---

## Soporte

Si un asistente reporta problemas:
1. Verificar en el admin si tiene el campo `dni_update_token` asignado
2. Si no lo tiene, ejecutar nuevamente `fix_dni.py`
3. Reenviar el email desde el admin
4. Si el enlace no funciona, verificar que el token sea correcto

---

**Documentación creada:** 28 de octubre de 2025  
**Versión:** 1.0  
**Estado:** Implementado y listo para producción
