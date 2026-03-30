#!/bin/bash
# Script de diagnóstico para el servidor del Congreso UNAB

echo "--- 1. Memoria RAM y Swap ---"
free -h
echo ""
swapon --show
echo ""

echo "--- 2. Uso de Disco ---"
df -h /
echo ""

echo "--- 3. Recursos de CPU ---"
lscpu | grep "CPU(s):" | head -n 1
uptime
echo ""

echo "--- 4. Procesos que más consumen (Top 10) ---"
ps -eo pmem,pcpu,comm --sort=-pmem | head -n 11
echo ""

echo "--- 5. Errores recientes de Nginx/Gunicorn ---"
# tail -n 10 /var/log/nginx/error.log 2>/dev/null || echo "No se pudo leer log de Nginx"
# journalctl -u congreso --no-pager -n 10 2>/dev/null || echo "No se pudo leer log de Gunicorn"
