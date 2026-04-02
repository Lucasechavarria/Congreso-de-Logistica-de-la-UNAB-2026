#!/bin/bash

# ==============================================================================
# SCRIPT DE MANTENIMIENTO SEMANAL - CONGRESO UNAB 2026
# Este script está diseñado para ejecutarse vía CRON (root)
# Frecuencia recomendada: Domingos 03:00 AM
# ==============================================================================

PROJECT_PATH="/var/www/congreso"
BACKUP_PATH="$PROJECT_PATH/backups"
LOG_DIR="/var/log"
DATE=$(date +%Y%m%d_%H%M%S)

echo "--- Iniciando mantenimiento semanal ($DATE) ---"

# 1. Crear directorio de backups si no existe
mkdir -p "$BACKUP_PATH"
chown -R www-data:www-data "$BACKUP_PATH"

# 2. Backup de la Base de Datos (PostgreSQL)
echo "[1/5] Generando backup de base de datos..."
su - postgres -c "pg_dump -Fc congreso_2026 > $BACKUP_PATH/backup_semanal_$DATE.dump"
# Mantener solo los últimos 4 backups (un mes)
ls -t $BACKUP_PATH/backup_semanal_*.dump | tail -n +5 | xargs rm -f -- 2>/dev/null

# 3. Limpieza de Sesiones y Cache de Django
echo "[2/5] Limpiando sesiones expiradas en la base de datos..."
$PROJECT_PATH/backend/env/bin/python $PROJECT_PATH/backend/manage.py clearsessions

# 4. Limpieza de Basura (Python Cache, __pycache__, logs temporales)
echo "[3/5] Eliminando archivos temporales y cache de Python..."
find $PROJECT_PATH/backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find $PROJECT_PATH/backend -name "*.pyc" -delete 2>/dev/null

# 5. Rotación/Limpieza de Logs
echo "[4/5] Truncando logs de diagnóstico y limpiando logs de Nginx..."
truncate -s 0 $PROJECT_PATH/backend/static/diag.txt

# Si somos root (vía cron), podemos limpiar logs del sistema
if [ -d "/var/log/nginx" ]; then
    find /var/log/nginx/ -name "*.gz" -mtime +30 -delete 2>/dev/null
    find /var/log/nginx/ -name "*.1" -delete 2>/dev/null
fi

# 6. Reinicio de Seguridad de Servicios (Para limpiar fugas de memoria)
echo "[5/5] Reiniciando servicios para purgar memoria..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "--- Mantenimiento completado con éxito ($DATE) ---"
echo "Log final en $PROJECT_PATH/backend/static/diag.txt"
