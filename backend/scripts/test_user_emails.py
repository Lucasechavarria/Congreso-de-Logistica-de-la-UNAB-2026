import os
import django
import sys
from datetime import date

# Añadir el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') # Ajustar si el nombre es diferente
django.setup()

from api.models import Asistente, Certificado, Edicion, Inscripcion
from api.email import send_certificate_email, send_broadcast_batch_email
from django.utils import timezone

def run_test():
    test_email = "echavarrialucas1986@gmail.com"
    print(f"Iniciando pruebas para: {test_email}")

    # 1. Obtener edición activa
    edicion_activa = Edicion.objects.filter(activa=True).first()
    if not edicion_activa:
        print("[ERROR] No hay edición activa.")
        return

    # 2. Buscar o crear asistente de prueba
    asistente, created = Asistente.objects.get_or_create(
        email=test_email,
        defaults={
            'first_name': 'Lucas',
            'last_name': 'Echavarria',
            'dni': '12345678',
            'profile_type': 'VISITOR',
            'asistencia_confirmada': True,
            'fecha_confirmacion': timezone.now()
        }
    )
    if created:
        print(f"Creado asistente de prueba: {asistente}")
    else:
        asistente.asistencia_confirmada = True
        asistente.fecha_confirmacion = timezone.now()
        asistente.save()
        print(f"Usando asistente existente: {asistente}")

    # Asegurar inscripción en la edición activa
    Inscripcion.objects.get_or_create(asistente=asistente, edicion=edicion_activa)

    # 3. Prueba de Certificado
    print("\n--- PRUEBA 1: Certificado ---")
    cert, cert_created = Certificado.objects.get_or_create(
        asistente=asistente,
        tipo_certificado='ASISTENCIA'
    )
    # Resetear estado para forzar re-envío si ya existía
    cert.email_enviado = False
    cert.save()

    print(f"Generando y enviando certificado...")
    success_cert = send_certificate_email(cert)
    if success_cert:
        print("[OK] Email de certificado enviado exitosamente.")
    else:
        print("[ERROR] Falló el envío del certificado.")

    # 4. Prueba de Broadcast
    print("\n--- PRUEBA 2: Broadcast (Masivo) ---")
    subject = "Prueba de Broadcast - Congreso 2026"
    body_html = """
    <h1>Hola Lucas!</h1>
    <p>Esta es una prueba del sistema de <strong>Broadcast</strong> (envío masivo) actualizado para el 2026.</p>
    <p>Si recibes este email con el logo correctamente embebido, la prueba es un éxito.</p>
    """
    
    enviados, errores = send_broadcast_batch_email([test_email], subject, body_html)
    if enviados > 0:
        print(f"[OK] Email de broadcast enviado exitosamente ({enviados}).")
    else:
        print(f"[ERROR] Falló el envío del broadcast ({errores} errores).")

    print("\nPruebas finalizadas.")

if __name__ == "__main__":
    run_test()
