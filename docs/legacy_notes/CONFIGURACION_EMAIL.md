# Guía para Configurar Gmail SMTP con Django

## Problema Identificado

El email no llega porque Gmail requiere una **contraseña de aplicación específica** (16 caracteres) en lugar de tu contraseña normal para aplicaciones externas.

## Solución Paso a Paso

### 1. Preparar tu Cuenta de Google

1. **Accede a tu cuenta de Google:** [myaccount.google.com](https://myaccount.google.com/)
2. **Ve a "Seguridad"** en el menú lateral izquierdo
3. **Habilita la "Verificación en 2 pasos"** si no está activa:
   - Busca la sección "Verificación en 2 pasos"
   - Sigue los pasos para configurarla (necesitarás tu teléfono)

### 2. Generar Contraseña de Aplicación

1. **Una vez habilitada la verificación en 2 pasos**, ve a:
   [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

2. **Crea una nueva contraseña de aplicación:**
   - Selecciona "Otro (nombre personalizado)"
   - Escribe: "Django Congreso UNAB"
   - Haz clic en "GENERAR"

3. **Copia la contraseña de 16 caracteres** que aparece (algo como: `abcd efgh ijkl mnop`)

### 3. Actualizar la Configuración

1. **Abre el archivo `.env`** en el directorio backend
2. **Reemplaza la línea `EMAIL_HOST_PASSWORD`** con la nueva contraseña:

   ```
   EMAIL_HOST_PASSWORD=abcdefghijklmnop
   ```

   (Sin espacios, solo los 16 caracteres)

3. **Guarda el archivo**

### 4. Cambiar a SMTP Backend

En el archivo `backend/core/settings.py`, cambia:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Por:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

### 5. Probar el Sistema

Ejecuta el script de diagnóstico:

```bash
cd backend
python test_email.py
```

## Configuración Final Esperada

Tu archivo `.env` debe verse así:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=contactofolkode@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop  # Contraseña de aplicación de 16 caracteres
EMAIL_USE_TLS=True
```

## Posibles Problemas y Soluciones

### Error de Autenticación

- **Causa:** Contraseña incorrecta o no es contraseña de aplicación
- **Solución:** Generar nueva contraseña de aplicación

### Email va a Spam

- **Causa:** Gmail puede marcar emails automáticos como spam
- **Solución:** Revisar carpeta de spam en el email de destino

### "Less secure app access"

- **Causa:** Método obsoleto, ya no funciona
- **Solución:** Usar contraseñas de aplicación (este método)

### No puedo encontrar "Contraseñas de aplicación"

- **Causa:** Verificación en 2 pasos no está habilitada
- **Solución:** Habilitar verificación en 2 pasos primero

## Información Adicional

- Las contraseñas de aplicación son específicas por aplicación
- Son de 16 caracteres sin espacios
- Se pueden revocar individualmente
- No afectan tu contraseña principal de Google
- Son más seguras que usar tu contraseña principal

## Script de Diagnóstico

El archivo `test_email.py` puede ayudarte a identificar problemas:

- Verifica la conexión SMTP
- Prueba el envío de emails básicos
- Prueba el sistema de certificados completo
- Proporciona diagnósticos detallados
