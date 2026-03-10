#!/usr/bin/env python3
"""
Script para limpiar y validar el campo DNI de los asistentes en la base de datos.

1. Elimina caracteres no numéricos.
2. Si el DNI tiene 9 dígitos y termina en 0, elimina ese último 0.
3. Si el DNI no tiene exactamente 8 dígitos, lo deja en nulo.
4. Asigna token único a quienes no tienen DNI válido.
5. Elimina token a quienes sí tienen DNI válido.
6. Muestra un resumen de los asistentes afectados.
"""
import os
import sys
import django
import re
import secrets

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Asistente

def is_valid_dni(dni):
    """Devuelve True si el DNI es exactamente 8 dígitos numéricos."""
    return bool(dni and len(dni) == 8 and dni.isdigit())

def clean_dni():
    print("--- Limpieza y Validación de DNIs de Asistentes ---")

    todos = Asistente.objects.all()
    afectados = []
    for a in todos:
        original = a.dni or ''
        limpio = re.sub(r'\D', '', original)
        # Si tiene 9 dígitos y termina en 0, eliminar el último 0
        if len(limpio) == 9 and limpio.endswith('0'):
            limpio = limpio[:-1]
        if is_valid_dni(limpio):
            nuevo = limpio
        else:
            nuevo = None
        if nuevo != original:
            afectados.append((a, original, nuevo))

    print(f"\n[INFO] {len(afectados)} asistentes con DNI a limpiar/corregir:")
    for a, original, nuevo in afectados:
        print(f"  - ID: {a.id}, Nombre: {a.first_name} {a.last_name}, DNI original: '{original}' -> '{nuevo}'")

    confirm = input("\n¿Deseas aplicar estos cambios? (s/n): ").lower()
    if confirm != 's':
        print("[CANCELADO] No se realizaron cambios.")
        return

    # Aplicar cambios de DNI (sin validación automática para evitar conflictos)
    for a, _, nuevo in afectados:
        # Usar update en lugar de save para evitar la validación automática
        Asistente.objects.filter(id=a.id).update(dni=nuevo)
    print(f"\n[SUCCESS] Se corrigieron {len(afectados)} DNIs.")

    # Asignar/eliminar tokens según corresponda
    print("\n[INFO] Asignando tokens a quienes no tienen DNI válido y eliminando tokens a quienes sí lo tienen...")
    sin_dni = Asistente.objects.filter(dni__isnull=True) | Asistente.objects.filter(dni='')
    con_dni = Asistente.objects.exclude(dni__isnull=True).exclude(dni='')

    # Eliminar token a quienes ya tienen DNI válido
    for a in con_dni:
        if a.dni_update_token:
            Asistente.objects.filter(id=a.id).update(dni_update_token=None)

    # Asignar token único a quienes no tienen DNI válido
    for a in sin_dni:
        if not a.dni_update_token:
            token = secrets.token_urlsafe(32)
            Asistente.objects.filter(id=a.id).update(dni_update_token=token)

    # Recargar los asistentes sin DNI para mostrar el token actualizado
    sin_dni = Asistente.objects.filter(dni__isnull=True) | Asistente.objects.filter(dni='')
    
    # Mostrar listado de emails+token para quienes deben corregir su DNI
    print(f"\n[RESUMEN] {sin_dni.count()} asistentes sin DNI válido tras la limpieza (listos para email):")
    for a in sin_dni:
        print(f"  - Email: {a.email} | Token: {a.dni_update_token}")

if __name__ == "__main__":
    clean_dni()