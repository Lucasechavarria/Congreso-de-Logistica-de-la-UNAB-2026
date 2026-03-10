import os
import django
from django.conf import settings

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Asistente, Empresa, PostulacionDisertante, Inscripcion
from api.email import (
    send_individual_confirmation_email, 
    send_empresa_confirmation_email, 
    send_postulacion_disertante_email
)

def test_emails():
    test_email = 'echavarrialucas1986@gmail.com'
    
    print(f"--- Iniciando envío de pruebas a {test_email} ---")

    # 1. Prueba Email Asistente
    try:
        # Buscamos un asistente existente o creamos uno temporal
        asistente, _ = Asistente.objects.get_or_create(
            email=test_email,
            defaults={
                'first_name': 'Lucas',
                'last_name': 'Echavarria',
                'dni': '32764773',
                'profile_type': Asistente.ProfileType.VISITOR
            }
        )
        success_asistente = send_individual_confirmation_email(asistente)
        print(f"1. Email Asistente: {'ENVIADO' if success_asistente else 'FALLO'}")
    except Exception as e:
        print(f"Error en prueba 1: {e}")

    # 2. Prueba Email Empresa
    try:
        empresa = Empresa(
            nombre_empresa='Empresa de Prueba UNAB',
            nombre_contacto='Lucas Echavarria',
            email_contacto=test_email
        )
        # Nota: No guardamos en DB para no ensuciar, pasamos la instancia
        success_empresa = send_empresa_confirmation_email(empresa)
        print(f"2. Email Empresa: {'ENVIADO' if success_empresa else 'FALLO'}")
    except Exception as e:
        print(f"Error en prueba 2: {e}")

    # 3. Prueba Email Disertante
    try:
        postulacion = PostulacionDisertante(
            nombre_apellido='Lucas Echavarria',
            email=test_email,
            titulo_charla='Innovación en Logística 4.0',
            ejes_tematicos=['Tecnología', 'Transporte']
        )
        success_disertante = send_postulacion_disertante_email(postulacion)
        print(f"3. Email Disertante (CFP): {'ENVIADO' if success_disertante else 'FALLO'}")
    except Exception as e:
        print(f"Error en prueba 3: {e}")

    print("--- Fin de las pruebas ---")

if __name__ == "__main__":
    test_emails()
