import os
import django
from django.utils import timezone
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Asistente, Empresa

def count_today():
    today = datetime(2026, 3, 20).date()
    # Asistentes
    asistentes = Asistente.objects.filter(fecha_registro__date=today)
    # Empresas
    empresas = Empresa.objects.filter(fecha_registro__date=today)
    
    print(f"Asistentes hoy: {asistentes.count()}")
    print(f"Empresas hoy: {empresas.count()}")
    
    for a in asistentes:
        print(f" - Asistente: {a.first_name} {a.last_name} ({a.email}) - Perfil: {a.profile_type}")
    
    for e in empresas:
        print(f" - Empresa: {e.nombre_empresa} ({e.email_contacto})")

if __name__ == "__main__":
    count_today()
