#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_with_correct_count():
    """Prueba con la cantidad correcta de miembros"""
    print("🧪 Probando con cantidad correcta de miembros...")
    
    data = {
        "first_name": "Dario",
        "last_name": "Gimenez", 
        "dni": "32522833",
        "email": "daseg2109@gmail.com",
        "phone": "11-1234-5678",
        "profile_type": "GROUP_REPRESENTATIVE",
        "group_name": "Instituto de Logística Nacional",
        "group_municipality": "Buenos Aires",
        "group_size": 2,  # Cantidad: 2
        "miembros_grupo_nuevos": [
            {
                "first_name": "Victoria",
                "last_name": "Gimenez",
                "dni": "31444396",
                "email": "victoria@gmail.com"
            },
            {
                "first_name": "Segundo",
                "last_name": "Miembro",
                "dni": "98765432",
                "email": "segundo@gmail.com"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/participantes/", json=data)
    
    print(f"Código de respuesta: {response.status_code}")
    print(f"Respuesta: {response.text}")
    
    if response.status_code == 201:
        print("✅ ¡Inscripción exitosa!")
        
        # Verificar que se crearon correctamente
        list_response = requests.get(f"{BASE_URL}/participantes/")
        if list_response.status_code == 200:
            participantes = list_response.json()
            representante = next((p for p in participantes if p['dni'] == '32522833'), None)
            if representante:
                print(f"Representante: {representante['first_name']} {representante['last_name']}")
                print(f"Miembros representados: {len(representante.get('miembros_representados', []))}")
                for miembro in representante.get('miembros_representados', []):
                    print(f"  - {miembro['first_name']} {miembro['last_name']} (DNI: {miembro['dni']})")
    else:
        print("❌ Error en la inscripción")

if __name__ == "__main__":
    test_with_correct_count()
