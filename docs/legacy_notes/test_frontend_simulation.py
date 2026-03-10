#!/usr/bin/env python3

import requests
import json

# Simular exactamente lo que envía el frontend después de nuestros cambios
BASE_URL = "http://127.0.0.1:8000/api"

def test_frontend_group_registration():
    """Simula exactamente lo que envía el frontend"""
    print("🧪 Simulando inscripción grupal desde el frontend...")
    
    # Datos exactos que enviaría el frontend
    data = {
        "first_name": "Dario",
        "last_name": "Gimenez", 
        "dni": "32522833",
        "email": "daseg2109@gmail.com",
        "phone": "11-1234-5678",
        "profile_type": "GROUP_REPRESENTATIVE",
        "group_name": "Instituto de Logística Nacional",
        "group_municipality": "Buenos Aires",
        "group_size": 2,
        "miembros_grupo_nuevos": [
            {
                "first_name": "Victoria",
                "last_name": "Gimenez",
                "dni": "31444396",
                "email": "daseg2109@gmail.com"
            }
        ]
    }
    
    print(f"Datos a enviar: {json.dumps(data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/participantes/", json=data)
    
    print(f"Código de respuesta: {response.status_code}")
    print(f"Respuesta: {response.text}")
    
    if response.status_code == 201:
        print("✅ ¡Inscripción exitosa!")
        result = response.json()
        return result.get('id')
    else:
        print("❌ Error en la inscripción")
        return None

if __name__ == "__main__":
    test_frontend_group_registration()
