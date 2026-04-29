import os
import django
import sys

# Configurar entorno Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from api.models import Disertante, PostulacionDisertante

def create_restricted_admin():
    username = 'Brenda'
    password = 'Brenda.2026'
    
    # Crear o actualizar usuario
    user, created = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = False
    user.save()
    
    # Limpiar y asignar permisos de solo lectura
    user.user_permissions.clear()
    ct_postulacion = ContentType.objects.get_for_model(PostulacionDisertante)
    ct_disertante = ContentType.objects.get_for_model(Disertante)

    perm_view_postulacion = Permission.objects.get(codename='view_postulaciondisertante', content_type=ct_postulacion)
    perm_view_disertante = Permission.objects.get(codename='view_disertante', content_type=ct_disertante)

    user.user_permissions.add(perm_view_postulacion, perm_view_disertante)
    print(f"Usuario {username} configurado exitosamente en la base de datos.")

if __name__ == "__main__":
    try:
        create_restricted_admin()
        # AUTO-ELIMINACIÓN por seguridad
        script_path = os.path.abspath(__file__)
        os.remove(script_path)
        print("El script se ha auto-eliminado correctamente tras la ejecución.")
    except Exception as e:
        print(f"Error al ejecutar el script: {e}")
