#!/usr/bin/env python
"""Script de prueba para el nuevo sistema de inscripción grupal."""
import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Asistente
from django.test import RequestFactory
from django.http import JsonResponse
from api.views import RegistroParticipantesView

#!/usr/bin/env python3
import requests
import json
import time

def test_email_sending():
    """
    Prueba específica para verificar que los emails se envían correctamente
    """
    print("=== PRUEBA DE ENVÍO DE EMAILS ===")
    
    # Usar emails reales para poder verificar la recepción
    url = "http://localhost:8000/api/participantes/"
    
    # Inscripción grupal con emails reales
    data = {
        "first_name": "Test",
        "last_name": "Representante", 
        "dni": "99999999",
        "email": "dgimenez.developer@gmail.com",  # Email real para verificar
        "phone": "1234567890",
        "profile_type": "GROUP_REPRESENTATIVE",
        "group_name": "Grupo de Prueba Email",
        "group_municipality": "Test City",
        "group_size": 2,
        "miembros_grupo_nuevos": [
            {
                "first_name": "Test",
                "last_name": "Miembro1",
                "dni": "88888888",
                "email": "dgimenez.developer+test1@gmail.com"  # Email con alias
            },
            {
                "first_name": "Test",
                "last_name": "Miembro2", 
                "dni": "77777777",
                "email": "dgimenez.developer+test2@gmail.com"  # Email con alias
            }
        ]
    }
    
    print("Enviando inscripción grupal con emails reales...")
    print(f"📧 Emails que deberían recibir confirmación:")
    print(f"  - Representante: {data['email']}")
    for miembro in data['miembros_grupo_nuevos']:
        print(f"  - Miembro: {miembro['email']}")
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 201:
            print("\n✅ Inscripción grupal exitosa")
            print("⏳ Esperando unos segundos para el envío de emails...")
            time.sleep(3)
            print("📧 Los emails deberían haber sido enviados desde: congresologisticaytransporte@unab.edu.ar")
            return True
        else:
            print(f"❌ Error en inscripción: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_new_group_system():
    """
    Prueba el nuevo sistema de inscripción grupal donde:
    1. Se especifica la cantidad de miembros
    2. Se crean asistentes individuales automáticamente
    3. Cada miembro puede generar QR y certificado individual
    4. Se envían emails de confirmación a todos los miembros
    """
    
    # URL del endpoint
    url = "http://localhost:8000/api/participantes/"
    
    # Datos del representante y miembros del grupo
    data = {
        "first_name": "Dario",
        "last_name": "Gimenez", 
        "dni": "12345678",
        "email": "dgimenez.developer@gmail.com",
        "phone": "1234567890",
        "profile_type": "GROUP_REPRESENTATIVE",
        "group_name": "Asociación de Transportistas del Sur",
        "group_municipality": "Almirante Brown",
        "group_size": 2,
        "miembros_grupo_nuevos": [
            {
                "first_name": "Juan",
                "last_name": "Pérez",
                "dni": "11111111",
                "email": "juan.perez@email.com"
            },
            {
                "first_name": "María",
                "last_name": "González", 
                "dni": "22222222",
                "email": "maria.gonzalez@email.com"
            }
        ]
    }
    
    print("=== PRUEBA DEL NUEVO SISTEMA DE INSCRIPCIÓN GRUPAL CON EMAILS ===")
    print(f"Enviando datos a: {url}")
    print(f"Representante: {data['first_name']} {data['last_name']} - {data['email']}")
    print(f"Grupo: {data['group_name']}")
    print(f"Cantidad de miembros: {data['group_size']}")
    print(f"Miembros: {len(data['miembros_grupo_nuevos'])}")
    for i, miembro in enumerate(data['miembros_grupo_nuevos'], 1):
        print(f"  {i}. {miembro['first_name']} {miembro['last_name']} - {miembro['email']}")
    
    print(f"\n📧 Se deberían enviar emails a:")
    print(f"  - Representante: {data['email']}")
    for miembro in data['miembros_grupo_nuevos']:
        print(f"  - Miembro: {miembro['email']}")
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        print(f"\nCódigo de respuesta: {response.status_code}")
        print(f"Respuesta: {response.text}")
        
        if response.status_code == 201:
            print("\n✅ ¡ÉXITO! Inscripción grupal realizada correctamente")
            print("📧 Los emails de confirmación deberían haber sido enviados")
            
            # Ahora verificamos que se crearon los asistentes individuales
            print("\n=== VERIFICACIÓN DE ASISTENTES CREADOS ===")
            
            # Obtener lista de asistentes para verificar
            list_url = "http://localhost:8000/api/participantes/"
            list_response = requests.get(list_url)
            
            if list_response.status_code == 200:
                asistentes = list_response.json()
                
                # Buscar el representante
                representante = None
                miembros = []
                
                for asistente in asistentes:
                    if (asistente.get('dni') == data['dni'] and 
                        asistente.get('profile_type') == 'GROUP_REPRESENTATIVE'):
                        representante = asistente
                    elif asistente.get('profile_type') == 'VISITOR' and asistente.get('representante_grupo'):
                        # Es un miembro del grupo
                        if any(m['dni'] == asistente.get('dni') for m in data['miembros_grupo_nuevos']):
                            miembros.append(asistente)
                
                if representante:
                    print(f"Representante: {representante['first_name']} {representante['last_name']}")
                    print(f"Miembros representados: {len(representante.get('miembros_representados', []))}")
                    
                print(f"Miembros individuales creados: {len(miembros)}")
                for miembro in miembros:
                    print(f"  - {miembro['first_name']} {miembro['last_name']} (ID: {miembro['id']}) - {miembro.get('email', 'N/A')}")
                
                if len(miembros) == data['group_size']:
                    print("\n✅ Todos los miembros fueron creados correctamente como asistentes individuales")
                    print("📧 Revisa tu bandeja de entrada para verificar que llegaron los emails de confirmación")
                else:
                    print(f"\n❌ Error: Se esperaban {data['group_size']} miembros, pero se crearon {len(miembros)}")
            
        else:
            print(f"\n❌ Error en la inscripción: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalles del error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Respuesta del servidor: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error de conexión: {e}")

def test_individual_registration():
    """
    Prueba la inscripción individual para verificar que también se envían emails
    """
    url = "http://localhost:8000/api/participantes/"
    
    data = {
        "first_name": "Ana",
        "last_name": "López",
        "dni": "33333333",
        "email": "ana.lopez@email.com", 
        "phone": "1122334455",
        "profile_type": "STUDENT",
        "is_unab_student": True,
        "career": "Ingeniería en Logística",
        "year_of_study": 3
    }
    
    print("\n=== PRUEBA DE INSCRIPCIÓN INDIVIDUAL CON EMAIL ===")
    print(f"Inscribiendo estudiante: {data['first_name']} {data['last_name']} - {data['email']}")
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        print(f"Código de respuesta: {response.status_code}")
        print(f"Respuesta: {response.text}")
        
        if response.status_code == 201:
            print("✅ ¡ÉXITO! Inscripción individual realizada correctamente")
            print("📧 El email de confirmación debería haber sido enviado")
        else:
            print(f"❌ Error en la inscripción: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE EMAILS\n")
    
    # Prueba específica de envío de emails
    email_success = test_email_sending()
    
    print("\n" + "="*60)
    
    # Pruebas del sistema completo
    test_new_group_system()
    test_individual_registration()
    
    print("\n" + "="*60)
    if email_success:
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("📧 Verifica tu bandeja de entrada para confirmar la recepción de emails")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        
    print("\n💡 Los emails se envían desde: congresologisticaytransporte@unab.edu.ar")
