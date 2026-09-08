# Generated manually to update fields and insert/update postulación for GERMAN MENICHETTI

from django.db import migrations, models


def crear_o_actualizar_postulacion_german_menichetti(apps, schema_editor):
    PostulacionDisertante = apps.get_model('api', 'PostulacionDisertante')
    Edicion = apps.get_model('api', 'Edicion')

    edicion = Edicion.objects.filter(activa=True).first()
    if not edicion:
        edicion = Edicion.objects.filter(anio=2026).first()
    if not edicion:
        edicion = Edicion.objects.order_by('-id').first()

    nombre = "GERMAN MENICHETTI"
    titulo = "Infraestructura vial inteligente: cómo la telemetría transforma la gestión urbana a nivel municipal"
    resumen = "evidencia para la planificación y gestión de infraestructura vial urbana en municipios bonaerenses"

    # Buscar primero por ID 13 o por nombre
    postulacion = PostulacionDisertante.objects.filter(id=13).first()
    if not postulacion:
        postulacion = PostulacionDisertante.objects.filter(nombre_apellido__icontains="GERMAN MENICHETTI").first()

    if postulacion:
        postulacion.nombre_apellido = nombre
        postulacion.titulo_charla = titulo
        postulacion.resumen_charla = resumen
        postulacion.objetivos_charla = resumen
        postulacion.edicion = edicion
        if not postulacion.estado:
            postulacion.estado = 'PENDIENTE'
        postulacion.acepta_tyc = True
        postulacion.save()
    else:
        PostulacionDisertante.objects.create(
            nombre_apellido=nombre,
            titulo_charla=titulo,
            resumen_charla=resumen,
            objetivos_charla=resumen,
            edicion=edicion,
            estado='PENDIENTE',
            acepta_tyc=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0049_disertante_empresa_institucion_programa_estado_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postulaciondisertante',
            name='dni',
            field=models.CharField(blank=True, db_index=True, default='', max_length=20, verbose_name='DNI / Documento'),
        ),
        migrations.AlterField(
            model_name='postulaciondisertante',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='Email de contacto'),
        ),
        migrations.AlterField(
            model_name='postulaciondisertante',
            name='telefono',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Teléfono'),
        ),
        migrations.AlterField(
            model_name='postulaciondisertante',
            name='ciudad_provincia',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Ciudad y Provincia'),
        ),
        migrations.AlterField(
            model_name='postulaciondisertante',
            name='profesion_cargo',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Profesión / Cargo actual'),
        ),
        migrations.AlterField(
            model_name='postulaciondisertante',
            name='resumen_charla',
            field=models.TextField(blank=True, default='', verbose_name='Resumen de la charla (máx. 300 palabras)'),
        ),
        migrations.AlterField(
            model_name='postulaciondisertante',
            name='objetivos_charla',
            field=models.TextField(blank=True, default='', verbose_name='Objetivos de la exposición'),
        ),
        migrations.RunPython(crear_o_actualizar_postulacion_german_menichetti, reverse_code=migrations.RunPython.noop),
    ]
