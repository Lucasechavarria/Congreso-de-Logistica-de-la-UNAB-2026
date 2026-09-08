# Migration 0050: Flexibilizar campos y restaurar la información histórica original de la postulación 13 (Germán Menichetti)

from django.db import migrations, models


def restaurar_info_historica_german_menichetti(apps, schema_editor):
    PostulacionDisertante = apps.get_model('api', 'PostulacionDisertante')
    HistoricalPostulacionDisertante = apps.get_model('api', 'HistoricalPostulacionDisertante')
    Edicion = apps.get_model('api', 'Edicion')

    edicion = Edicion.objects.filter(activa=True).first() or Edicion.objects.filter(anio=2026).first() or Edicion.objects.order_by('-id').first()

    # 1. Intentar obtener el registro actual (ID 13 o por nombre)
    postulacion = PostulacionDisertante.objects.filter(id=13).first()
    if not postulacion:
        postulacion = PostulacionDisertante.objects.filter(nombre_apellido__icontains="GERMAN MENICHETTI").first()

    # 2. Buscar en la tabla de historial (HistoricalPostulacionDisertante) la versión original previa a cualquier modificación
    historial_original = HistoricalPostulacionDisertante.objects.filter(id=13).order_by('history_date').first()
    if not historial_original:
        historial_original = HistoricalPostulacionDisertante.objects.filter(nombre_apellido__icontains="GERMAN MENICHETTI").order_by('history_date').first()

    if postulacion and historial_original:
        # Restaurar absolutamente todos los campos originales desde el historial de la DB
        postulacion.nombre_apellido = historial_original.nombre_apellido or postulacion.nombre_apellido
        postulacion.dni = historial_original.dni or postulacion.dni
        postulacion.email = historial_original.email or postulacion.email
        postulacion.telefono = historial_original.telefono or postulacion.telefono
        postulacion.ciudad_provincia = historial_original.ciudad_provincia or postulacion.ciudad_provincia
        postulacion.profesion_cargo = historial_original.profesion_cargo or postulacion.profesion_cargo
        postulacion.empresa_institucion = historial_original.empresa_institucion or postulacion.empresa_institucion
        postulacion.linkedin = historial_original.linkedin or postulacion.linkedin
        postulacion.titulo_charla = historial_original.titulo_charla or postulacion.titulo_charla
        postulacion.ejes_tematicos = historial_original.ejes_tematicos or postulacion.ejes_tematicos
        postulacion.eje_otro = historial_original.eje_otro or postulacion.eje_otro
        postulacion.resumen_charla = historial_original.resumen_charla or postulacion.resumen_charla
        postulacion.objetivos_charla = historial_original.objetivos_charla or postulacion.objetivos_charla
        postulacion.publico_dirigido = historial_original.publico_dirigido or postulacion.publico_dirigido
        postulacion.modalidad = historial_original.modalidad or postulacion.modalidad
        postulacion.participacion_tipo = historial_original.participacion_tipo or postulacion.participacion_tipo
        postulacion.experiencia_previa = historial_original.experiencia_previa or postulacion.experiencia_previa
        postulacion.duracion_estimada = historial_original.duracion_estimada or postulacion.duracion_estimada
        postulacion.requiere_equipamiento = historial_original.requiere_equipamiento or postulacion.requiere_equipamiento
        postulacion.edicion = historial_original.edicion or edicion
        postulacion.save()
    elif not postulacion and historial_original:
        # Re-crear el registro a partir del snapshot del historial si fue borrado o no existe
        PostulacionDisertante.objects.create(
            id=13,
            edicion=historial_original.edicion or edicion,
            nombre_apellido=historial_original.nombre_apellido,
            dni=historial_original.dni or '',
            email=historial_original.email or '',
            telefono=historial_original.telefono or '',
            ciudad_provincia=historial_original.ciudad_provincia or '',
            profesion_cargo=historial_original.profesion_cargo or '',
            empresa_institucion=historial_original.empresa_institucion or '',
            linkedin=historial_original.linkedin,
            titulo_charla=historial_original.titulo_charla or 'Infraestructura vial inteligente',
            ejes_tematicos=historial_original.ejes_tematicos or '',
            eje_otro=historial_original.eje_otro,
            resumen_charla=historial_original.resumen_charla or '',
            objetivos_charla=historial_original.objetivos_charla or '',
            publico_dirigido=historial_original.publico_dirigido or '',
            modalidad=historial_original.modalidad or '',
            participacion_tipo=historial_original.participacion_tipo or '',
            experiencia_previa=historial_original.experiencia_previa,
            duracion_estimada=historial_original.duracion_estimada or 30,
            requiere_equipamiento=historial_original.requiere_equipamiento,
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
        migrations.RunPython(restaurar_info_historica_german_menichetti, reverse_code=migrations.RunPython.noop),
    ]
