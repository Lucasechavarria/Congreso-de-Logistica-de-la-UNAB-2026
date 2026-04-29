from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_brenda_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # Modelos de la API
    # Usamos strings para evitar problemas de importación circular en migraciones
    Disertante = apps.get_model('api', 'Disertante')
    PostulacionDisertante = apps.get_model('api', 'PostulacionDisertante')

    # Crear o actualizar el usuario Brenda
    user, created = User.objects.get_or_create(username='Brenda')
    user.password = make_password('Brenda.2026')
    user.is_staff = True
    user.is_active = True
    user.is_superuser = False
    user.save()

    # Obtener permisos de vista
    try:
        ct_postulacion = ContentType.objects.get_for_model(PostulacionDisertante)
        ct_disertante = ContentType.objects.get_for_model(Disertante)

        perm_view_postulacion = Permission.objects.get(codename='view_postulaciondisertante', content_type=ct_postulacion)
        perm_view_disertante = Permission.objects.get(codename='view_disertante', content_type=ct_disertante)

        user.user_permissions.add(perm_view_postulacion, perm_view_disertante)
    except Exception:
        # Si los permisos no existen aún en este punto de la migración, se asignarán manualmente después
        # pero normalmente ya existen para el modelo 0044
        pass

def remove_brenda_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='Brenda').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0044_alter_disertante_linkedin_alter_empresa_sitio_web_and_more'),
    ]

    operations = [
        migrations.RunPython(create_brenda_user, reverse_code=remove_brenda_user),
    ]
