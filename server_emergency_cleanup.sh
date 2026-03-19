# Comandos de Emergencia para Liberar Espacio (root)

### 1. Limpieza de Logs y APT (Crítico)
```bash
# Limpiar logs de más de 1 día
journalctl --vacuum-time=1d
# Limpiar cache de paquetes
apt-get clean
# Borrar archivos temporales antiguos
rm -rf /tmp/*
```

### 2. Identificar archivos grandes
```bash
du -sh /* 2>/dev/null | sort -h
```

### 3. Reducir trabajadores de Gunicorn
Si tienes poca RAM, reduce el número de workers en tu archivo de servicio (probablemente `/etc/systemd/system/congreso.service`).
Busca la línea `ExecStart` y asegúrate de que `--workers` no sea mayor a 2 o 3.
