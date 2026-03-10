#!/usr/bin/env python
"""
Script para diagnosticar y probar el envío de emails del sistema de certificados.
"""
import os
import django
import smtplib

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from api.models import Asistente, Certificado
from api.email import send_certificate_email

def test_smtp_connection():
    """Test directo de conexión SMTP"""
    print("🔍 Probando conexión SMTP directa...")
    try:
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()  # Habilitar TLS
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.quit()
        print("✅ Conexión SMTP exitosa")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación SMTP: {e}")
        print("💡 Probable causa: Necesitas una contraseña de aplicación de Gmail")
        print("📋 Solución: Ir a https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        print(f"❌ Error de conexión SMTP: {e}")
        return False

def test_basic_email():
    """Test básico de envío de email"""
    print("🔍 Probando envío de email básico...")
    try:
        send_mail(
            'Test de email del sistema',
            'Este es un email de prueba del sistema de certificados.',
            settings.DEFAULT_FROM_EMAIL,
            ['dgimenez.developer@gmail.com'],
            fail_silently=False,
        )
        print("✅ Email básico enviado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error enviando email básico: {e}")
        return False

def test_certificate_email():
    """Test del sistema de certificados"""
    print("🔍 Probando sistema de certificados...")
    try:
        # Buscar un asistente existente
        asistente = Asistente.objects.filter(email='dgimenez.developer@gmail.com').first()
        if not asistente:
            print("❌ No se encontró el asistente con email dgimenez.developer@gmail.com")
            return False
        
        # Buscar o crear certificado
        certificado, created = Certificado.objects.get_or_create(
            asistente=asistente,
            tipo_certificado=Certificado.TipoCertificado.ASISTENCIA
        )
        
        # Enviar certificado por email
        send_certificate_email(certificado)
        print("✅ Certificado enviado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error enviando certificado: {e}")
        return False

def show_email_config():
    """Mostrar configuración actual de email"""
    print("📧 Configuración actual de email:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    password_masked = settings.EMAIL_HOST_PASSWORD[:4] + "*" * (len(settings.EMAIL_HOST_PASSWORD) - 4) if settings.EMAIL_HOST_PASSWORD else "No configurada"
    print(f"   EMAIL_HOST_PASSWORD: {password_masked}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

def diagnose_email_issues():
    """Diagnóstico completo de problemas de email"""
    print("🔧 Ejecutando diagnóstico completo...")
    
    issues = []
    
    # Verificar configuración básica
    if not settings.EMAIL_HOST_USER:
        issues.append("EMAIL_HOST_USER no está configurado")
    
    if not settings.EMAIL_HOST_PASSWORD:
        issues.append("EMAIL_HOST_PASSWORD no está configurado")
    
    if settings.EMAIL_HOST_PASSWORD and len(settings.EMAIL_HOST_PASSWORD) != 16:
        issues.append("EMAIL_HOST_PASSWORD debe ser una contraseña de aplicación de 16 caracteres")
    
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        issues.append("EMAIL_BACKEND está configurado para console (modo desarrollo)")
    
    if issues:
        print("⚠️  Problemas encontrados:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("✅ Configuración básica correcta")
    
    return len(issues) == 0

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico del sistema de email...")
    print("=" * 60)
    
    show_email_config()
    print("=" * 60)
    
    # Diagnóstico básico
    config_ok = diagnose_email_issues()
    print()
    
    if config_ok:
        # Test de conexión SMTP
        smtp_test = test_smtp_connection()
        print()
        
        if smtp_test:
            # Test básico
            basic_test = test_basic_email()
            print()
            
            # Test de certificado
            cert_test = test_certificate_email()
            print()
            
            if basic_test and cert_test:
                print("🎉 ¡Todos los tests pasaron exitosamente!")
            else:
                print("❌ Algunos tests fallaron, pero la conexión SMTP funciona")
        else:
            print("🛑 No se puede continuar sin conexión SMTP válida")
    
    print("\n� Pasos para solucionar problemas:")
    print("1. Habilitar verificación en 2 pasos en tu cuenta de Google")
    print("2. Generar contraseña de aplicación en: https://myaccount.google.com/apppasswords")
    print("3. Actualizar EMAIL_HOST_PASSWORD en .env con la contraseña de 16 caracteres")
    print("4. Cambiar EMAIL_BACKEND a 'django.core.mail.backends.smtp.EmailBackend'")
    print("5. Ejecutar este script nuevamente para verificar")
