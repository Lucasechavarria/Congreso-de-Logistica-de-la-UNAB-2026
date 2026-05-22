import os
import sys
import django

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Asistente, Inscripcion, Edicion

print("Total asistentes en BD:", Asistente.objects.count())
print("Ediciones:")
for ed in Edicion.objects.all():
    print(f"- {ed.nombre} ({ed.anio}), Activa: {ed.activa}, Inscripciones: {ed.inscripciones.count()}")

# Buscar si existe Frizzotti
frizz = Asistente.objects.filter(last_name__icontains="Frizzotti").first()
if frizz:
    print("Encontrado Frizzotti:", frizz.first_name, frizz.last_name, frizz.email, frizz.dni)
else:
    print("No se encontró Frizzotti")

# Buscar docentes/estudiantes de ISDFYT 83
from api.models import DetalleEstudiante, DetalleDocente
print("Total DetalleEstudiante:", DetalleEstudiante.objects.count())
print("Total DetalleDocente:", DetalleDocente.objects.count())
