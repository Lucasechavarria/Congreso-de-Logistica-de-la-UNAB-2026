import os
import django
import sys
import random
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Asistente, Edicion
from api.email import _generar_excel_miembros, send_individual_confirmation_email

def test_excel_generation():
    print("Testing Excel generation...")
    rnd = random.randint(10000000, 99999999)
    email = f"test_rep_{rnd}@example.com"
    dni = str(rnd)
    
    # Create a representative
    try:
        rep = Asistente.objects.create(
            email=email,
            first_name="Test",
            last_name="Representative",
            dni=dni,
            profile_type=Asistente.ProfileType.GROUP_REPRESENTATIVE
        )
        print(f"Representative created: {email} (DNI: {dni})")
        
        # Add some members
        # Using a fixed 8-digit DNI for members
        Asistente.objects.create(
            email=f"member1_{rnd}@example.com",
            first_name="Member1",
            last_name="One",
            dni=str(random.randint(20000000, 29999999)),
            representante_grupo=rep,
            profile_type=Asistente.ProfileType.VISITOR
        )
        print("Member added.")
        
        # Generate Excel
        output = _generar_excel_miembros(rep)
        filename = f"test_group_members_{rnd}.xlsx"
        with open(filename, "wb") as f:
            f.write(output.getvalue())
        print(f"Excel successfully generated: {filename}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_alert_logic():
    print("\nTesting Alert Logic execution...")
    rnd = random.randint(30000000, 39999999)
    # Test Press - Should NOT crash
    press = Asistente(
        email=f"press_{rnd}@example.com", 
        first_name="P", 
        last_name="R", 
        profile_type=Asistente.ProfileType.PRESS,
        dni=str(rnd)
    )
    # We don't save, just test the email function
    send_individual_confirmation_email(press)
    print("Press email logic execution: OK")

if __name__ == "__main__":
    try:
        test_excel_generation()
        test_alert_logic()
    finally:
        # Cleanup any generated files for this test run in the script itself if desired
        pass
