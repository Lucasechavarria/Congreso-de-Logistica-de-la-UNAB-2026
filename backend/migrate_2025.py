import os
import sys
import django # type: ignore
import pandas as pd # type: ignore
from datetime import datetime

# Añadir el directorio actual al path para que Django pueda cargar los modelos
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Asistente, DetalleEstudiante, DetalleDocente, DetalleProfesional, DetalleGrupo, Edicion # type: ignore

def migrate_2025_data(csv_path):
    """
    Migra datos desde un CSV (exportado de la tabla api_asistente de 2025)
    hacia el nuevo esquema normalizado de 2026.
    """
    # Intentar cargar la edición 2025
    edicion_2025, _ = Edicion.objects.get_or_create(
        anio=2025, 
        defaults={'nombre': 'Edición 2025', 'activa': False}
    )

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return

    count = 0
    errors = 0

    for index, row in df.iterrows():
        try:
            # 1. Crear Asistente base
            asistente, created = Asistente.objects.get_or_create(
                email=row['email'],
                defaults={
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'phone': row['phone'] if pd.notna(row['phone']) else None,
                    'dni': str(row['dni']) if pd.notna(row['dni']) else None,
                    'profile_type': row['profile_type'],
                    'asistencia_confirmada': bool(row['asistencia_confirmada']),
                    'fecha_confirmacion': row['fecha_confirmacion'] if pd.notna(row['fecha_confirmacion']) else None,
                    'rol_especifico': row['rol_especifico'] if pd.notna(row['rol_especifico']) else None,
                }
            )

            if not created:
                print(f"Asistente ya existe: {row['email']}")
                continue

            # 2. Crear detalles según el profile_type
            ptype = row['profile_type']

            if ptype == 'STUDENT':
                DetalleEstudiante.objects.create(
                    asistente=asistente,
                    is_unab_student=bool(row.get('is_unab_student', False)),
                    institution=row.get('institution'),
                    career=row.get('career'),
                    year_of_study=row.get('year_of_study') if pd.notna(row.get('year_of_study')) else None
                )
            
            elif ptype == 'TEACHER':
                DetalleDocente.objects.create(
                    asistente=asistente,
                    institution=row.get('institution'),
                    career_taught=row.get('career_taught')
                )

            elif ptype == 'PROFESSIONAL':
                DetalleProfesional.objects.create(
                    asistente=asistente,
                    work_area=row.get('work_area'),
                    occupation=row.get('occupation')
                )

            elif ptype == 'GROUP_REPRESENTATIVE':
                DetalleGrupo.objects.create(
                    asistente=asistente,
                    group_name=row.get('group_name'),
                    group_municipality=row.get('group_municipality'),
                    group_size=row.get('group_size', 0)
                )

            count += 1
            if count % 100 == 0:
                print(f"Procesados {count} registros...")

        except Exception as e:
            print(f"Error procesando fila {index} ({row.get('email')}): {e}")
            errors += 1

    print(f"\nMigración completada:")
    print(f"- Éxitos: {count}")
    print(f"- Errores: {errors}")

if __name__ == "__main__":
    # Nombre del archivo CSV que el usuario debe generar desde el backup SQL
    CSV_FILE = 'asistentes_2025.csv'
    if os.path.exists(CSV_FILE):
        migrate_2025_data(CSV_FILE)
    else:
        print(f"Por favor, exporta la tabla 'api_asistente' de 2025 a un archivo '{CSV_FILE}'")
        print("Puedes usar: SELECT * FROM api_asistente INTO OUTFILE '/var/lib/mysql-files/asistentes_2025.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n';")
