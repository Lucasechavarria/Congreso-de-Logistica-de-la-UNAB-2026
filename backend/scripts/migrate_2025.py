import os
import sys
import re
import django
import pandas as pd
from datetime import datetime

# Añadir el directorio actual al path para que Django pueda cargar los modelos
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Asistente, DetalleEstudiante, DetalleDocente, DetalleProfesional, DetalleGrupo, Edicion, Inscripcion

def clean_dni(dni):
    if pd.isna(dni) or str(dni).strip().upper() == 'NULL':
        return None
    # Eliminar todo lo que no sea número
    dni_str = re.sub(r'\D', '', str(dni))
    # Caso común: 9 dígitos terminados en 0
    if len(dni_str) == 9 and dni_str.endswith('0'):
        dni_str = dni_str[:8]
    # Retornar SOLO si tiene exactamente 7 u 8 dígitos (regla de negocio)
    if 7 <= len(dni_str) <= 8:
        return dni_str
    return None

def clean_phone(phone):
    if pd.isna(phone) or str(phone).strip().upper() == 'NULL':
        return None
    phone_str = str(phone).strip()
    # Dejar solo números (regla de negocio: solo numérico)
    phone_cleaned = re.sub(r'[^0-9]', '', phone_str)
    # Limitar a 20 estrictos
    return phone_cleaned[:20]

def migrate_2025_data(csv_path):
    print(f"Iniciando migración desde {csv_path}...")
    
    # 1. Obtener edición 2025
    edicion_2025, _ = Edicion.objects.get_or_create(
        anio=2025, 
        defaults={'nombre': 'Congreso 2025', 'activa': False}
    )

    # 2. Leer CSV con fallbacks de encoding
    columns = ['email', 'first_name', 'last_name', 'phone', 'dni', 'profile_type', 
               'asistencia_confirmada', 'fecha_confirmacion', 'rol_especifico']
    
    df = None
    # Probamos latin1 (muy común en exports de Windows/Excel en Latam)
    # Probamos utf-8-sig (para archivos con BOM)
    # Probamos utf-8
    for enc in ['latin1', 'utf-8-sig', 'utf-8']:
        try:
            df = pd.read_csv(csv_path, encoding=enc, names=columns, header=None)
            print(f"Archivo cargado con éxito usando encoding: {enc}")
            break
        except Exception:
            continue
            
    if df is None:
        print("ERROR: No se pudo leer el archivo con ninguna codificación conocida (latin1, utf-8).")
        return

    count = 0
    errors = 0
    skipped = 0

    for index, row in df.iterrows():
        email = str(row['email']).strip().lower()
        if not email or email == 'null':
            skipped += 1
            continue

        try:
            # Limpieza de datos
            dni_cleaned = clean_dni(row['dni'])
            phone_cleaned = clean_phone(row['phone'])
            first_name = str(row['first_name'])[:100] if pd.notna(row['first_name']) else "Sin nombre"
            last_name = str(row['last_name'])[:100] if pd.notna(row['last_name']) else "Sin apellido"
            
            # 1. Crear o actualizar Asistente
            asistente, created = Asistente.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone_cleaned,
                    'dni': dni_cleaned,
                    'profile_type': row['profile_type'] if pd.notna(row['profile_type']) else 'VISITOR',
                    'asistencia_confirmada': bool(row['asistencia_confirmada']) if pd.notna(row['asistencia_confirmada']) else False,
                    'fecha_confirmacion': row['fecha_confirmacion'] if pd.notna(row['fecha_confirmacion']) else None,
                    'rol_especifico': row['rol_especifico'] if pd.notna(row['rol_especifico']) else None,
                }
            )

            # 2. Registrar inscripción para la edición 2025
            Inscripcion.objects.get_or_create(
                asistente=asistente,
                edicion=edicion_2025
            )

            count += 1
            if count % 100 == 0:
                print(f"Procesados {count} registros...")

        except Exception as e:
            print(f"Error procesando fila {index + 1} ({email}): {e}")
            errors += 1

    print(f"\nMigración completada:")
    print(f"- Exitosos: {count}")
    print(f"- Errores: {errors}")
    print(f"- Saltados (sin email): {skipped}")

if __name__ == "__main__":
    CSV_FILE = 'asistentes_2025.csv'
    if os.path.exists(CSV_FILE):
        migrate_2025_data(CSV_FILE)
    else:
        print(f"ERROR: No se encuentra el archivo '{CSV_FILE}' en el directorio actual.")
        print("Asegúrate de copiar el CSV al servidor (/var/www/congreso/backend/)")
