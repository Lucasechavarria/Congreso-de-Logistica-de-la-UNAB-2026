from django.db import migrations

def copy_disertante_to_disertantes(apps, schema_editor):
    Programa = apps.get_model('api', 'Programa')
    for programa in Programa.objects.all():
        if programa.disertante_old_id:
            programa.disertantes.add(programa.disertante_old_id)

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0015_remove_programa_disertante_programa_disertante_old_and_more'),
    ]

    operations = [
        migrations.RunPython(copy_disertante_to_disertantes, reverse_code=migrations.RunPython.noop),
    ]
