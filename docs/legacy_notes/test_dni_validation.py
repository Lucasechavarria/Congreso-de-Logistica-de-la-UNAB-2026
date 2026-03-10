#!/usr/bin/env python3
"""
Script para probar la validación de DNI en el modelo y serializer.
"""
import os
import sys
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Asistente
from api.serializers import AsistenteSerializer
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

def test_model_validation():
    print("\n--- Prueba de validación en el modelo ---")
    
    # Caso 1: DNI válido (8 dígitos)
    try:
        a = Asistente(
            first_name="Test",
            last_name="User",
            email="test_valid@example.com",
            phone="1234567890",
            dni="12345678",
            profile_type="VISITOR"
        )
        a.full_clean()
        print("✓ DNI válido '12345678' pasó la validación")
    except ValidationError as e:
        print(f"✗ DNI válido '12345678' falló: {e}")
    
    # Caso 2: DNI con 9 dígitos y termina en 0 (debe limpiarse automáticamente)
    try:
        a = Asistente(
            first_name="Test",
            last_name="User",
            email="test_9digits@example.com",
            phone="1234567890",
            dni="123456780",
            profile_type="VISITOR"
        )
        a.full_clean()
        print(f"✓ DNI '123456780' se limpió automáticamente a '{a.dni}'")
    except ValidationError as e:
        print(f"✗ DNI '123456780' falló: {e}")
    
    # Caso 3: DNI inválido (menos de 8 dígitos)
    try:
        a = Asistente(
            first_name="Test",
            last_name="User",
            email="test_invalid_short@example.com",
            phone="1234567890",
            dni="123456",
            profile_type="VISITOR"
        )
        a.full_clean()
        print("✗ DNI inválido '123456' NO fue rechazado (ERROR)")
    except ValidationError as e:
        print(f"✓ DNI inválido '123456' fue rechazado correctamente")
    
    # Caso 4: DNI con caracteres no numéricos
    try:
        a = Asistente(
            first_name="Test",
            last_name="User",
            email="test_letters@example.com",
            phone="1234567890",
            dni="1234567a",
            profile_type="VISITOR"
        )
        a.full_clean()
        print("✗ DNI con letras '1234567a' NO fue rechazado (ERROR)")
    except ValidationError as e:
        print(f"✓ DNI con letras '1234567a' fue rechazado correctamente")

def test_serializer_validation():
    print("\n--- Prueba de validación en el serializer ---")
    
    # Caso 1: DNI válido
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test_serializer_valid@example.com",
        "phone": "1234567890",
        "dni": "87654321",
        "profile_type": "VISITOR"
    }
    serializer = AsistenteSerializer(data=data)
    try:
        serializer.is_valid(raise_exception=True)
        print(f"✓ DNI válido '87654321' pasó la validación del serializer")
    except DRFValidationError as e:
        print(f"✗ DNI válido '87654321' falló: {e}")
    
    # Caso 2: DNI inválido (menos de 8 dígitos)
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test_serializer_invalid@example.com",
        "phone": "1234567890",
        "dni": "123456",
        "profile_type": "VISITOR"
    }
    serializer = AsistenteSerializer(data=data)
    try:
        serializer.is_valid(raise_exception=True)
        print("✗ DNI inválido '123456' NO fue rechazado por el serializer (ERROR)")
    except DRFValidationError as e:
        print(f"✓ DNI inválido '123456' fue rechazado correctamente por el serializer")

if __name__ == "__main__":
    test_model_validation()
    test_serializer_validation()
    print("\n--- Pruebas completadas ---")
