import os
import django
import random
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Asistente, InscripcionPrensa, Edicion
from api.email import send_admin_postulation_alert

def verify_unified_alerts():
    print("Verifying Unified Admin Alerts...")
    rnd = random.randint(1000, 9999)
    
    # Use a fixed 8-digit DNI to comply with validation
    dni_press = f"11{rnd}111"[:8]
    dni_rep = f"22{rnd}222"[:8]
    dni_member = f"33{rnd}333"[:8]

    # 1. Test Press Alert
    print("\n[Testing Press Alert]")
    press = InscripcionPrensa(
        nombre_apellido="Periodista de Prueba",
        dni=dni_press,
        email=f"press_test_{rnd}@example.com",
        telefono="12345678",
        tipo_perfil="PERIODISTA",
        medio_o_canal="Diario Digital Antigravity",
        url_perfil_red="https://ig.com/antigravity",
        url_sitio_medio="https://antigravity.news"
    )
    press.save()
    success_press = send_admin_postulation_alert(press, "Prensa")
    print(f"Press Alert Result: {'SUCCESS' if success_press else 'FAILED'}")

    # 2. Test Group Alert
    print("\n[Testing Group Alert]")
    # Using string literal for profile_type to be safe
    rep = Asistente.objects.create(
        email=f"rep_test_{rnd}@example.com",
        first_name="Representante",
        last_name="Prueba",
        dni=dni_rep,
        profile_type='GROUP_REPRESENTATIVE',
        terminos_aceptados=True
    )
    # Add DetalleGrupo
    from api.models import DetalleGrupo
    DetalleGrupo.objects.create(
        asistente=rep,
        group_name="Institución de Prueba",
        group_size=5
    )
    
    # Add a member to ensure Excel generation doesn't fail
    Asistente.objects.create(
        email=f"member_test_{rnd}@example.com",
        first_name="Miembro",
        last_name="Test",
        dni=dni_member,
        representante_grupo=rep,
        profile_type='VISITOR', # Must have a profile type
        terminos_aceptados=True
    )
    
    success_group = send_admin_postulation_alert(rep, "Grupo")
    print(f"Group Alert Result: {'SUCCESS' if success_group else 'FAILED'}")

if __name__ == "__main__":
    try:
        verify_unified_alerts()
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
