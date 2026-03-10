#!/usr/bin/env python
"""
Script de prueba para enviar email individual con fecha correcta (15 de noviembre de 2025)
al usuario de prueba: Dario Sebastian Gimenez
"""

import os
import django
import sys

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/home/daro/Documentos/FolKode Group/proyectos/congreso/Congreso-UNAB/backend')
django.setup()

from api.models import Asistente
from api.email import send_bulk_confirmation_email

def test_email_individual():
    """Enviar email de prueba a Dario con fecha correcta"""
    try:
        # Buscar o crear el usuario de prueba
        email_prueba = "dgimenez.developer@gmail.com"
        
        asistente, created = Asistente.objects.get_or_create(
            email=email_prueba,
            defaults={
                'first_name': 'Dario Sebastian',
                'last_name': 'Gimenez',
                'dni': '32522833',
                'institution': 'FolKode Group',
                'profile_type': Asistente.ProfileType.PROFESSIONAL,
                'rol_especifico': 'Developer'
            }
        )
        
        print(f"[INFO] Usuario {'creado' if created else 'encontrado'}: {asistente.nombre_completo}")
        print(f"[INFO] Email: {asistente.email}")
        print(f"[INFO] DNI: {asistente.dni}")
        print(f"[INFO] Perfil: {asistente.get_profile_type_display()}")
        print(f"[INFO] Rol específico: {asistente.rol_especifico}")
        
        # Enviar email con fecha correcta: 15 de noviembre de 2025
        print(f"\n[INFO] Enviando email de prueba con fecha: 15 de noviembre de 2025...")
        resultado = send_bulk_confirmation_email(
            asistente,
            es_carga_masiva=True,
            es_recordatorio=False,
            fecha_evento='2025-11-15'
        )
        
        if resultado:
            print(f"✅ [SUCCESS] Email enviado exitosamente a {asistente.email}")
            print(f"📧 Verifica tu bandeja de entrada para confirmar que la fecha es correcta:")
            print(f"   - Fecha esperada: 15 de noviembre de 2025")
            print(f"   - Email de destino: {asistente.email}")
        else:
            print(f"❌ [ERROR] Falló el envío del email")
            
    except Exception as e:
        print(f"❌ [ERROR] Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email_individual()
