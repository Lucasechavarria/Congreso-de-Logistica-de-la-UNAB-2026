import os
import django
import sys

# Add backend directory to sys.path
sys.path.append(os.getcwd())

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Edicion

def ensure_active_edition():
    active = Edicion.objects.filter(activa=True).first()
    if active:
        print(f"OK: Edicion activa encontrada: {active.nombre} ({active.anio})")
    else:
        # Check if 2026 exists
        ed2026 = Edicion.objects.filter(anio=2026).first()
        if ed2026:
            ed2026.activa = True
            ed2026.save()
            print(f"FIXED: Edicion 2026 encontrada y marcada como activa.")
        else:
            try:
                Edicion.objects.create(nombre="Congreso de Logística UNAB 2026", anio=2026, activa=True)
                print(f"FIXED: Edicion 2026 no existía. Creada y marcada como activa.")
            except Exception as e:
                print(f"ERROR: No se pudo crear la edición: {e}")

if __name__ == "__main__":
    ensure_active_edition()
