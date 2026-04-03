import os
import django
import sys
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.serializers import InscripcionSerializer

def manual_test():
    dni_rep = f"99{random.randint(100000, 999999)}"
    data = {
        "asistente": {
            "first_name": "Test",
            "last_name": "Rep",
            "dni": dni_rep,
            "email": f"test_rep_{dni_rep}@example.com",
            "phone": "87654321",
            "profile_type": "GROUP_REPRESENTATIVE",
            "group_name": "Test Group",
            "group_size": 2,
            "terminos_aceptados": True,
            "miembros_grupo_nuevos": [
                {
                    "first_name": "Member1",
                    "last_name": "One",
                    "dni": f"33{random.randint(100000, 999999)}",
                    "email": f"member1_{dni_rep}@example.com"
                },
                {
                    "first_name": "Member2",
                    "last_name": "Two",
                    "dni": f"44{random.randint(100000, 999999)}",
                    "email": f"member2_{dni_rep}@example.com"
                }
            ]
        }
    }
    
    try:
        serializer = InscripcionSerializer(data=data)
        if serializer.is_valid():
            print("Serializer is valid (Group)")
            obj = serializer.save()
            print(f"Created success (Group): {obj}")
        else:
            print(f"Serializer errors (Group): {serializer.errors}")
    except Exception as e:
        print(f"Exception during Group serialization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    manual_test()
