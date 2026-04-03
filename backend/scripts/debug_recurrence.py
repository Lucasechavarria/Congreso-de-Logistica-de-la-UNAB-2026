
import os
import sys
import django
from unittest.mock import patch

# Setup
PROJECT_ROOT = r'c:\Users\User\Desktop\Congreso-UNAB-main\backend'
sys.path.append(PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Asistente, Inscripcion, Edicion
from api.serializers import AsistenteSerializer

def debug_recurrence():
    try:
        # Limpiar BD de prueba si es necesario (suponiendo db.sqlite3 local)
        # Pero Django usa una BD de prueba diferente en tests reales.
        # Aquí usaremos la real, así que CUIDADO: crearemos registros de prueba.
        
        edicion_activa = Edicion.objects.filter(activa=True).first()
        if not edicion_activa:
            print("[ERROR] No hay edición activa.")
            return

        print(f"--- Depurando Recurrencia ---")
        print(f"Edición Activa: {edicion_activa}")

        # Simular inscripción antigua
        dni = "99887766"
        email = "test_recurrencia@test.com"
        
        # Primero borrar rastro si existe
        Asistente.objects.filter(dni=dni).delete()
        
        print("Creando asistente antiguo...")
        asistente = Asistente.objects.create(
            first_name="Viejo", last_name="User", dni=dni,
            email=email, profile_type="VISITOR"
        )
        
        edicion_2025, _ = Edicion.objects.get_or_create(anio=2025, defaults={'nombre': '2025'})
        Inscripcion.objects.create(asistente=asistente, edicion=edicion_2025, asistencia_confirmada=True)

        print("Llamando a Serializer para nueva edición...")
        data = {
            "first_name": "Viejo",
            "last_name": "User",
            "dni": dni,
            "email": email,
            "profile_type": "VISITOR",
            "terminos_aceptados": True
        }
        
        with patch('api.serializers.send_individual_confirmation_email', return_value=True):
            serializer = AsistenteSerializer(data=data)
            if serializer.is_valid():
                print("Serializer es válido. Guardando...")
                serializer.save()
                print("Guardado con éxito.")
            else:
                print(f"Serializer INVÁLIDO: {serializer.errors}")

        # Verificar inscripciones
        insc_count = Inscripcion.objects.filter(asistente=asistente).count()
        print(f"Total Inscripciones: {insc_count}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_recurrence()
