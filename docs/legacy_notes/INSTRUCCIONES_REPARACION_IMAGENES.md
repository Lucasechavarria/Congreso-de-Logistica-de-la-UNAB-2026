# Instrucciones para Reparar Imágenes de Disertantes en Producción

## Problema Detectado
Las imágenes de los disertantes no se mostraban correctamente en el programa debido a:
1. URLs mal formadas en la base de datos (rutas absolutas del servidor)
2. Falta de normalización en el backend
3. Inconsistencias en el manejo de URLs en el frontend

## Solución Implementada

### 1. Backend - Mejoras en el Serializer
**Archivo**: `backend/api/serializers.py`

El método `get_foto_url()` del `DisertanteSerializer` ahora:
- Normaliza automáticamente todas las URLs a formato HTTPS
- Maneja múltiples formatos de entrada (rutas absolutas, relativas, URLs completas)
- Garantiza que siempre se devuelvan URLs válidas

### 2. Frontend - Función Mejorada
**Archivo**: `client/pages/Programa.tsx`

La función `getDisertanteImageUrl()` ahora:
- Maneja mejor los casos edge de URLs mal formadas
- Prioriza URLs HTTPS absolutas
- Tiene mejor logging de errores para debugging

### 3. Script de Migración
**Archivo**: `backend/api/management/commands/fix_disertante_urls.py`

Limpia las URLs existentes en la base de datos de producción.

## Pasos para Aplicar en Producción

### Paso 1: Hacer backup de la base de datos
```bash
# Conectarse al servidor de producción
ssh usuario@servidor

# Navegar al directorio del proyecto
cd /ruta/al/proyecto/backend

# Hacer backup de la base de datos
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
```

### Paso 2: Actualizar el código
```bash
# En tu máquina local, commitear y pushear los cambios
git add .
git commit -m "Fix: Reparar visualización de imágenes de disertantes"
git push origin main

# En el servidor de producción, actualizar el código
git pull origin main
```

### Paso 3: Activar el entorno virtual
```bash
source env/bin/activate  # o el path correcto del venv
```

### Paso 4: Ejecutar el script de migración (primero en dry-run)
```bash
# Ver qué cambios se aplicarían SIN modificar la BD
python manage.py fix_disertante_urls --dry-run
```

### Paso 5: Aplicar los cambios reales
```bash
# Si todo se ve bien, ejecutar sin --dry-run
python manage.py fix_disertante_urls
```

### Paso 6: Reiniciar el servidor
```bash
# Dependiendo de cómo esté configurado el servidor
sudo systemctl restart gunicorn  # o
sudo systemctl restart uwsgi     # o
pm2 restart all                  # o el comando que corresponda
```

### Paso 7: Limpiar caché del frontend (si aplica)
```bash
# Si hay caché de Vite/build
cd ../client
npm run build  # Reconstruir el frontend
```

### Paso 8: Verificar en producción
1. Abrir el sitio web: https://www.congresologistica.unab.edu.ar
2. Ir a la página de Programa
3. Abrir el modal de una charla que tenga disertantes
4. Verificar que las imágenes se muestren correctamente
5. Abrir la consola del navegador (F12) para ver si hay errores

## Verificación Post-Deploy

### En la consola del navegador
Las imágenes que no carguen mostrarán un log con:
```
Error cargando imagen del disertante: {
  nombre: "Nombre del disertante",
  foto_url_original: "URL original de la BD",
  foto_url_procesada: "URL procesada por la función"
}
```

### Comprobar las URLs en la API
```bash
# Desde el servidor o con curl
curl https://www.congresologistica.unab.edu.ar/api/programa/ | jq '.[0].disertantes'
```

Las URLs de foto_url deberían ser:
- `https://www.congresologistica.unab.edu.ar/media/ponencias/nombre.png` (formato completo)
- O `ponencias/nombre.png` (formato relativo que el frontend convierte)

## Rollback (si algo sale mal)

```bash
# Restaurar el backup de la base de datos
cp db.sqlite3.backup.FECHA db.sqlite3

# Volver a la versión anterior del código
git reset --hard COMMIT_ANTERIOR

# Reiniciar el servidor
sudo systemctl restart gunicorn
```

## Notas Adicionales

- ✅ Los cambios son backward-compatible (las URLs antiguas seguirán funcionando)
- ✅ No se requieren migraciones de Django
- ✅ El script puede ejecutarse múltiples veces sin problemas
- ✅ Las imágenes físicas NO se modifican, solo las URLs en la BD

## Contacto
Si hay problemas durante el deploy, revisar:
1. Logs del servidor web
2. Logs de Django (si están configurados)
3. Consola del navegador
4. Network tab para ver las URLs reales que se están solicitando
