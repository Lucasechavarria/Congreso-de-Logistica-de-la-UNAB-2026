import os
import django
import sys
import traceback

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.serializers import InscripcionSerializer

def manual_test():
    data = {
        "asistente": {
            "first_name": "Test",
            "last_name": "Traceback",
            "dni": "99887766",
            "email": "test_tb@example.com",
            "phone": "123",
            "profile_type": "VISITOR",
            "terminos_aceptados": True
        }
    }
    
    try:
        serializer = InscripcionSerializer(data=data)
        if serializer.is_valid():
            print("Serializer is valid")
            obj = serializer.save()
            print(f"Created success: {obj}")
        else:
            print(f"Serializer errors: {serializer.errors}")
    except Exception as e:
        print(f"Exception during serialization: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    manual_test()
