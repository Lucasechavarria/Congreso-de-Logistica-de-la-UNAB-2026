from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_remove_asistente_asistencia_confirmada_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='inscripcion',
            index=models.Index(fields=['edicion', 'asistencia_confirmada'], name='api_inscri_edicion_cf0db8_idx'),
        ),
        migrations.AddIndex(
            model_name='inscripcion',
            index=models.Index(fields=['fecha_inscripcion'], name='api_inscri_fecha_i_7f8486_idx'),
        ),
    ]
