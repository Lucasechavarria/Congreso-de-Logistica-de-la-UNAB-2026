import os
import django
from django.utils import timezone
from datetime import datetime, date
import argparse

# Configuración de entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Asistente, Empresa
from api.email import (
    send_individual_confirmation_email, 
    send_group_confirmation_emails, 
    send_empresa_confirmation_email
)

def resend_emails(target_date_str):
    try:
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    except ValueError:
        print("Error: El formato de fecha debe ser YYYY-MM-DD")
        return

    print(f"--- Reenviando inscripciones del día: {target_date} ---")

    # 1. Asistentes (Individuales y Representantes de Grupo)
    asistentes = Asistente.objects.filter(fecha_registro__date=target_date)
    count_asistentes = 0
    for a in asistentes:
        try:
            if a.profile_type == Asistente.ProfileType.GROUP_REPRESENTATIVE:
                print(f"Reenviando grupo de: {a.first_name} {a.last_name} ({a.email})")
                send_group_confirmation_emails(a)
            else:
                print(f"Reenviando individual a: {a.first_name} {a.last_name} ({a.email})")
                send_individual_confirmation_email(a)
            count_asistentes += 1
        except Exception as e:
            print(f"Error con asistente {a.email}: {e}")

    # 2. Empresas
    empresas = Empresa.objects.filter(fecha_registro__date=target_date)
    count_empresas = 0
    for e in empresas:
        try:
            print(f"Reenviando empresa: {e.nombre_empresa} ({e.email_contacto})")
            send_empresa_confirmation_email(e)
            count_empresas += 1
        except Exception as e:
            print(f"Error con empresa {e.nombre_empresa}: {e}")

    print(f"\n--- Resumen ---")
    print(f"Asistentes procesados: {count_asistentes}")
    print(f"Empresas procesadas: {count_empresas}")
    print("--- Fin del proceso ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reenviar emails de confirmación por fecha.")
    parser.add_argument("date", help="Fecha en formato YYYY-MM-DD")
    args = parser.parse_args()
    
    resend_emails(args.date)
