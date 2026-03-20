import os
import django
import sys

# Añadir el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings') # Ajustar si el nombre es diferente
django.setup()

from api.models import Edicion, Asistente, Inscripcion, Empresa, PostulacionDisertante, Disertante, InscripcionPrensa, Programa
from django.utils import timezone

def run():
    print("Iniciando configuración de ediciones...")
    
    # 1. Crear ediciones si no existen
    edicion_2025, created = Edicion.objects.get_or_create(
        anio=2025,
        defaults={'nombre': 'Congreso Logística 2025', 'activa': False}
    )
    if created:
        print("Creada Edición 2025.")
    
    edicion_2026, created = Edicion.objects.get_or_create(
        anio=2026,
        defaults={'nombre': 'Congreso Logística 2026', 'activa': True}
    )
    if created:
        print("Creada Edición 2026 (Activa).")
    else:
        # Asegurar que la 2026 sea la activa
        edicion_2026.activa = True
        edicion_2026.save()

    # 2. Migrar asistentes actuales a la edición 2025
    print("Migrando asistentes a la edición 2025...")
    asistentes = Asistente.objects.all()
    count_ins = 0
    for asistente in asistentes:
        if not Inscripcion.objects.filter(asistente=asistente, edicion=edicion_2025).exists():
            Inscripcion.objects.create(
                asistente=asistente,
                edicion=edicion_2025,
                fecha_inscripcion=asistente.fecha_registro or timezone.now()
            )
            count_ins += 1
    print(f"Se crearon {count_ins} inscripciones para la edición 2025.")

    # 3. Asignar edición 2025 a otros modelos que tengan edicion=None
    print("Asignando edición 2025 a registros huérfanos...")
    
    models_to_fix = [Empresa, PostulacionDisertante, Disertante, InscripcionPrensa, Programa]
    for model in models_to_fix:
        updated = model.objects.filter(edicion__isnull=True).update(edicion=edicion_2025)
        print(f"Actualizados {updated} registros de {model.__name__}.")

    print("Configuración finalizada con éxito.")

if __name__ == "__main__":
    run()
