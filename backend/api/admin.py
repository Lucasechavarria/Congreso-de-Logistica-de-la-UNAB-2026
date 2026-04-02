from django.contrib import admin
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.shortcuts import render
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils import timezone
import json
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Disertante, Empresa, Asistente, Inscripcion, Certificado, Programa, Dashboard, Edicion, PostulacionDisertante, InscripcionPrensa, MiembroGrupo
from django.shortcuts import redirect
from .email import send_certificate_email, send_broadcast_batch_email
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import transaction
import logging
import os

logger = logging.getLogger(__name__)


def get_stats_data(edicion_id=None, periodo='diario', entidad='inscripciones', fecha_desde=None, fecha_hasta=None):
    """
    Helper para obtener los datos de estadísticas, opcionalmente filtrados por edición
    y agrupados por un periodo específico.
    """
    # Obtener edición actual o seleccionada
    if edicion_id:
        try:
            edicion_actual = Edicion.objects.get(id=edicion_id)
        except (Edicion.DoesNotExist, ValueError):
            edicion_actual = Edicion.objects.filter(activa=True).first()
    else:
        edicion_actual = Edicion.objects.filter(activa=True).first()

    # Determinar la función de truncado
    if periodo == 'semanal':
        trunc_func = TruncWeek
        date_format = 'Semana #%W (%Y)'
    elif periodo == 'mensual':
        trunc_func = TruncMonth
        date_format = '%B %Y'
    else:
        trunc_func = TruncDate
        date_format = '%Y-%m-%d'

    # Preparar estructuras dinámicas
    main_stats = []
    distribution_stats = []

    if entidad == 'disertantes':
        # 1. Main Stats: Tendencia en el tiempo (Postulaciones)
        query = PostulacionDisertante.objects.all()
        if edicion_actual: query = query.filter(edicion=edicion_actual)
        if fecha_desde: query = query.filter(fecha_postulacion__date__gte=fecha_desde)
        if fecha_hasta: query = query.filter(fecha_postulacion__date__lte=fecha_hasta)
        stats_query = query.annotate(period=trunc_func('fecha_postulacion'))

        # 2. Distribution Stats: Estados de la postulación
        dist_raw = query.values('estado').annotate(value=Count('id'))
        estado_map = dict(PostulacionDisertante.ESTADO_CHOICES)
        distribution_stats = [
            {'name': estado_map.get(item['estado'], item['estado']), 'value': item['value']}
            for item in dist_raw
        ]

    elif entidad == 'empresas':
        # Empresas no tienen fecha_registro, usamos su modelo completo.
        query = Empresa.objects.all()
        if edicion_actual: query = query.filter(edicion=edicion_actual)
        if fecha_desde: query = query.filter(fecha_registro__date__gte=fecha_desde)
        # 1. Main Stats: Tendencia por fecha de registro
        stats_query = query.annotate(period=trunc_func('fecha_registro'))
        
        # 2. Distribution Stats: Estado de empresas
        dist_raw = query.values('estado').annotate(value=Count('id'))
        estado_map = dict(Empresa.ESTADO_CHOICES)
        distribution_stats = [
            {'name': estado_map.get(item['estado'], item['estado']), 'value': item['value']}
            for item in dist_raw
        ]

    else:
        # Por defecto Inscripciones
        query = Inscripcion.objects.all()
        if edicion_actual: query = query.filter(edicion=edicion_actual)
        if fecha_desde: query = query.filter(fecha_inscripcion__date__gte=fecha_desde)
        if fecha_hasta: query = query.filter(fecha_inscripcion__date__lte=fecha_hasta)
        stats_query = query.annotate(period=trunc_func('fecha_inscripcion'))

        # 2. Distribution Stats: Perfiles de los asistentes
        perfil_stats = Asistente.objects.all()
        if edicion_actual: perfil_stats = perfil_stats.filter(inscripciones__edicion=edicion_actual)
        dist_raw = perfil_stats.values('profile_type').annotate(value=Count('id', distinct=True))
        profile_map = dict(Asistente.ProfileType.choices)
        distribution_stats = [
            {'name': profile_map.get(item['profile_type'], item['profile_type']), 'value': item['value']}
            for item in dist_raw
        ]

    if stats_query is not None and not isinstance(stats_query, list):
        main_stats_raw = stats_query.values('period').annotate(count=Count('id')).order_by('period')
        
        running_total = 0
        main_stats = []
        for item in main_stats_raw:
            running_total += item['count']
            main_stats.append({
                'date': item['period'].strftime('%Y-%m-%d') if hasattr(item['period'], 'strftime') else str(item['period']), 
                'label': item['period'].strftime(date_format) if hasattr(item['period'], 'strftime') else str(item['period']),
                'count': item['count'],
                'cumulative': running_total
            })

    # 2. Comparativa por Edición (Totales)
    comparative_stats = []
    ediciones = Edicion.objects.all().order_by('anio')
    for ed in ediciones:
        comparative_stats.append({
            'name': f"{ed.nombre} ({ed.anio})",
            'total_inscritos': Inscripcion.objects.filter(edicion=ed).count(),
            'total_disertantes': Disertante.objects.filter(edicion=ed).count(),
            'total_empresas': Empresa.objects.filter(edicion=ed).count(),
        })

    # 4. Asistentes Recurrentes (Filtro por ediciones anteriores)
    recurrentes_count = 0
    if edicion_actual:
        asistentes_actuales = Asistente.objects.filter(inscripciones__edicion=edicion_actual).values_list('id', flat=True)
        asistentes_anteriores = Inscripcion.objects.exclude(edicion=edicion_actual).values_list('asistente_id', flat=True).distinct()
        recurrentes_count = Asistente.objects.filter(id__in=asistentes_actuales).filter(id__in=asistentes_anteriores).count()

    # 5. KPIs
    total_inscritos = Inscripcion.objects.filter(edicion=edicion_actual).count() if edicion_actual else 0
    total_disertantes = Disertante.objects.filter(edicion=edicion_actual).count() if edicion_actual else 0
    total_empresas = Empresa.objects.filter(edicion=edicion_actual).count() if edicion_actual else 0
    total_confirmados = Inscripcion.objects.filter(
        edicion=edicion_actual,
        asistencia_confirmada=True
    ).distinct().count() if edicion_actual else 0

    # 6. Nuevos KPIs de Velocidad
    hace_24h = timezone.now() - timezone.timedelta(hours=24)
    hace_7dias = timezone.now() - timezone.timedelta(days=7)
    
    registros_24h = (
        Inscripcion.objects.filter(edicion=edicion_actual, fecha_inscripcion__gte=hace_24h).count()
        if entidad == 'inscripciones' else
        Empresa.objects.filter(edicion=edicion_actual, fecha_registro__gte=hace_24h).count()
    ) if edicion_actual else 0

    return {
        'edicion_seleccionada': edicion_actual,
        'periodo_seleccionado': periodo,
        'entidad_seleccionada': entidad,
        'daily_stats': main_stats,
        'comparative_stats': comparative_stats,
        'distribution_stats': distribution_stats,
        'kpis': {
            'total_inscritos': total_inscritos,
            'total_confirmados': total_confirmados,
            'total_disertantes': total_disertantes,
            'total_empresas': total_empresas,
            'asistentes_recurrentes': recurrentes_count,
            'registros_24h': registros_24h,
            'promedio_diario': float(f"{main_stats[-1]['cumulative'] / max(1, len(main_stats)):.2f}") if main_stats else 0.0,
            'asistencia_ratio': float(f"{(total_confirmados / total_inscritos * 100):.2f}") if total_inscritos > 0 else 0.0
        },
        'todas_ediciones': Edicion.objects.all().order_by('-anio')
    }


def admin_dashboard(request):
    """
    Vista personalizada para el dashboard en el panel admin.
    """
    try:
        edicion_id = request.GET.get('edicion')
        periodo = request.GET.get('periodo', 'diario')
        entidad = request.GET.get('entidad', 'inscripciones')
        chart_type = request.GET.get('chart_type', 'line')
        chart_type_dist = request.GET.get('chart_type_dist', 'doughnut')
        fecha_desde = request.GET.get('fecha_desde', '')
        fecha_hasta = request.GET.get('fecha_hasta', '')
        
        stats = get_stats_data(
            edicion_id=edicion_id, 
            periodo=periodo, 
            entidad=entidad, 
            fecha_desde=fecha_desde if fecha_desde else None, 
            fecha_hasta=fecha_hasta if fecha_hasta else None
        )
        
        context = {
            **admin.site.each_context(request),
            'title': 'Power Dashboard Analysts',
            **stats,
            'chart_type_seleccionado': chart_type,
            'chart_type_dist_seleccionado': chart_type_dist,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'selected_id_list': [getattr(stats['edicion_seleccionada'], 'id', None)] if stats.get('edicion_seleccionada') else [],
            'selected_periodo_list': [periodo],
            'selected_entidad_list': [entidad],
            'selected_chart_type_list': [chart_type],
            'selected_chart_dist_list': [chart_type_dist],
            'daily_stats_json': json.dumps(stats['daily_stats']),
            'distribution_stats_json': json.dumps(stats['distribution_stats']),
            'comparative_stats_json': json.dumps(stats['comparative_stats']),
        }
        return render(request, 'admin/dashboard_power.html', context)
    except Exception as e:
        logger.error(f"Error in admin_dashboard: {str(e)}", exc_info=True)
        if settings.DEBUG:
            import traceback
            return HttpResponse(f"Error en Dashboard: {str(e)}<pre>{traceback.format_exc()}</pre>", status=500)
        return HttpResponse(f"Error interno al cargar el dashboard: {str(e)}. Consulte los logs del servidor.", status=500)


def broadcast_view(request):
    """
    Vista para el envío de comunicaciones masivas.
    """
    try:
        if request.method == 'POST':
            rol = request.POST.get('rol')
            asunto = request.POST.get('asunto')
            mensaje_html = request.POST.get('mensaje')

            emails = set()
            
            if rol == 'TODOS' or rol == 'ASISTENTES_TODOS':
                emails.update(Asistente.objects.values_list('email', flat=True))
            
            if rol == 'ASISTENTES_CONFIRMADOS':
                emails.update(Inscripcion.objects.filter(asistencia_confirmada=True).values_list('asistente__email', flat=True))
            
            if rol == 'TODOS' or rol == 'DISERTANTES':
                emails.update(PostulacionDisertante.objects.filter(estado='APROBADO').values_list('email', flat=True))
                
            if rol == 'TODOS' or rol == 'EMPRESAS':
                emails.update(Empresa.objects.filter(estado='APROBADO').values_list('email_contacto', flat=True))
                
            if rol == 'TODOS' or rol == 'PRENSA':
                emails.update(InscripcionPrensa.objects.values_list('email', flat=True))

            # Limpiar emails nulos o vacíos
            emails = [e for e in emails if e]

            if not emails:
                messages.error(request, "No se encontraron destinatarios para el filtro seleccionado.")
            else:
                enviados, errores = send_broadcast_batch_email(emails, asunto, mensaje_html)
                msg = f"Proceso finalizado. Enviados: {enviados}. Errores: {errores}."
                if errores == 0:
                    messages.success(request, msg)
                else:
                    messages.warning(request, msg)

        context = {
            **admin.site.each_context(request),
            'title': 'Comunicaciones Masivas',
        }
        return render(request, 'admin/email_masivo.html', context)
    except Exception as e:
        logger.error(f"Error in broadcast_view: {str(e)}", exc_info=True)
        if settings.DEBUG:
            import traceback
            return HttpResponse(f"Error en Broadcast: {str(e)}<pre>{traceback.format_exc()}</pre>", status=500)
        return HttpResponse(f"Error interno al cargar la vista de comunicaciones: {str(e)}. Consulte los logs del servidor.", status=500)
    

def backup_database_view(request):
    """
    Vista para descargar un backup (dump) completo de la base de datos PostgreSQL.
    Solo accesible para superusers.
    """
    if not request.user.is_superuser:
        return HttpResponse("No autorizado.", status=403)
        
    import subprocess
    from datetime import datetime
    
    try:
        # Obtener configuración de base de datos de Django
        from django.db import connection
        db_settings = connection.settings_dict
        
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_password = db_settings['PASSWORD']
        db_host = db_settings['HOST']
        db_port = db_settings['PORT']
        
        # Preparar el archivo temporal
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_congreso_{timestamp}.sql"
        
        # Ejecutar pg_dump
        # Nota: En producción suele requerir PGPASSWORD en el entorno
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password
        
        cmd = [
            'pg_dump',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-F', 'p',  # Formato plain text para .sql
            '-b',       # Incluir blobs
            '-v',       # Verbose
            db_name
        ]
        
        process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if isinstance(stderr, bytes) else str(stderr)
            logger.error(f"Error en pg_dump: {error_msg}")
            return HttpResponse(f"Error generando backup: {error_msg}", status=500)
            
        # Devolver el archivo como respuesta
        response = HttpResponse(stdout, content_type='application/sql')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        logger.error(f"Error en backup_database_view: {str(e)}", exc_info=True)
        return HttpResponse(f"Error interno: {str(e)}", status=500)

@admin.site.admin_view
def certificate_queue_view(request):
    """
    Muestra la interfaz de progreso para el envío de certificados.
    """
    pendientes = Certificado.objects.filter(email_enviado=False).count()
    return render(request, 'admin/certificate_queue.html', {'pendientes': pendientes})

@admin.site.admin_view
def process_certificate_batch_api(request):
    """
    JSON API para procesar un lote de certificados.
    """
    BATCH_SIZE = 5
    certificados = Certificado.objects.filter(email_enviado=False)[:BATCH_SIZE]
    
    logs = []
    processed = 0
    errors = 0
    
    for cert in certificados:
        try:
            # send_certificate_email ya se encarga de actualizar el estado en el modelo
            success = send_certificate_email(cert)
            if success:
                logs.append(f"Enviado con éxito a {cert.asistente.email}")
                processed += 1
            else:
                logs.append(f"Error enviando a {cert.asistente.email}")
                errors += 1
        except Exception as e:
            logs.append(f"Error crítico con {cert.asistente.email}: {str(e)}")
            errors += 1
            
    remaining = Certificado.objects.filter(email_enviado=False).count()
    
    return JsonResponse({
        'status': 'ok',
        'processed': processed,
        'errors': errors,
        'remaining': remaining,
        'logs': logs
    })


# Inyectar el dashboard en el Admin de Django
def patch_admin_urls():
    original_get_urls = admin.site.get_urls
    
    def get_urls(*args, **kwargs):
        urls = original_get_urls(*args, **kwargs)
        custom_urls = [
            path('dashboard/', admin.site.admin_view(admin_dashboard), name='admin-dashboard'),
            path('broadcast/', admin.site.admin_view(broadcast_view), name='admin-broadcast'),
            path('backup-db/', admin.site.admin_view(backup_database_view), name='admin-backup-db'),
            path('certificate-queue/', admin.site.admin_view(certificate_queue_view), name='admin-certificate-queue'),
            path('process-certificate-batch/', admin.site.admin_view(process_certificate_batch_api), name='process-certificate-batch'),
            path('manual-certificate/', admin.site.admin_view(manual_certificate_view), name='admin-manual-certificate'),
        ]
        return custom_urls + urls
    
    admin.site.get_urls = get_urls

patch_admin_urls()
# Cambiar el título del índice para incluir un link directo con estilo HTML
admin.site.index_title = format_html(
    'Admin Congreso - <a href="/admin/dashboard/" style="color: #a78bfa; text-decoration: underline;">Dashboard</a> | '
    '<a href="/admin/broadcast/" style="color: #fbbf24; text-decoration: underline;">Comunicaciones Masivas</a> | '
    '<a href="/admin/api/asistente/import-excel/" style="color: #4ade80; text-decoration: underline; font-weight: bold;">Carga Masiva Excel</a> | '
    '<a href="/admin/backup-db/" style="color: #f87171; text-decoration: underline;">Backup DB</a> | '
    '<a href="/admin/certificate-queue/" style="color: #4ade80; text-decoration: underline;">Cola Certificados</a> | '
    '<a href="/admin/manual-certificate/" style="color: #60a5fa; text-decoration: underline;">Certificado Manual</a>'
)
admin.site.site_header = "Congreso Logística UNAB 2026 Admin"
admin.site.site_title = "Panel Administrativo"




class DNIFilter(admin.SimpleListFilter):
    """
    Filtro personalizado para filtrar asistentes según si tienen o no DNI válido.
    """
    title = 'Estado DNI'
    parameter_name = 'dni_status'

    def lookups(self, request, model_admin):
        return [
            ('sin_dni', 'Sin DNI'),
            ('con_dni', 'Con DNI'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'sin_dni':
            # Filtrar asistentes sin DNI (nulo o vacío)
            return queryset.filter(dni__isnull=True) | queryset.filter(dni='')
        if self.value() == 'con_dni':
            # Filtrar asistentes con DNI válido (no nulo y no vacío)
            return queryset.exclude(dni__isnull=True).exclude(dni='')
        return queryset


class MiembroGrupoInline(admin.TabularInline):
    model = MiembroGrupo
    extra = 0
    readonly_fields = ('fecha_registro',)

def manual_certificate_view(request):
    """
    Vista para generar y enviar un certificado manualmente ingresando Nombre e Email.
    """
    if not request.user.is_staff:
        return HttpResponse("No autorizado.", status=403)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email_addr = request.POST.get('email')
        tipo = request.POST.get('tipo', 'ASISTENCIA')

        if not nombre or not email_addr:
            messages.error(request, "Nombre y Email son obligatorios.")
        else:
            try:
                # Buscamos si ya existe un asistente con ese email, si no creamos uno temporal
                asistente, _ = Asistente.objects.get_or_create(
                    email=email_addr,
                    defaults={'first_name': nombre.split(' ')[0], 'last_name': ' '.join(nombre.split(' ')[1:]) or '—'}
                )
                
                cert = Certificado(asistente=asistente, tipo_certificado=tipo)
                cert.save()
                
                # Usar la lógica de envío en memoria
                from .email import send_certificate_email
                result = send_certificate_email(cert)
                
                # Manejar retorno simple (bool) o tupla (bool, str) para compatibilidad
                success = result[0] if isinstance(result, tuple) else result
                error_msg = result[1] if isinstance(result, tuple) else "Error desconocido en el servidor de correo."
                
                if success:
                    messages.success(request, f"Certificado enviado exitosamente a {email_addr}.")
                else:
                    messages.error(request, f"Error al enviar el certificado a {email_addr}: {error_msg}")
            except Exception as e:
                messages.error(request, f"Error crítico: {str(e)}")

    context = {
        **admin.site.each_context(request),
        'title': 'Generación de Certificado Manual',
    }
    return render(request, 'admin/manual_certificate.html', context)

class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('asistente', 'empresa', 'fecha_inscripcion_detalle', 'edicion')
    list_filter = ('edicion', 'fecha_inscripcion')
    search_fields = ('asistente__first_name', 'asistente__last_name', 'asistente__email', 'empresa__razon_social')
    readonly_fields = ('fecha_inscripcion',)

    def fecha_inscripcion_detalle(self, obj):
        return obj.fecha_inscripcion.strftime("%d/%m/%Y %H:%M:%S") if obj.fecha_inscripcion else "-"
    fecha_inscripcion_detalle.short_description = 'Fecha Inscripción'
    fecha_inscripcion_detalle.admin_order_field = 'fecha_inscripcion'

class AsistenteAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'dni', 'get_ediciones', 'get_asistencia_actual', 'fecha_registro_detalle')
    list_filter = (DNIFilter, 'inscripciones__asistencia_confirmada', 'inscripciones__edicion', 'fecha_registro')
    search_fields = ('first_name', 'last_name', 'email', 'dni')

    def fecha_registro_detalle(self, obj):
        return obj.fecha_registro.strftime("%d/%m/%Y %H:%M:%S") if obj.fecha_registro else "-"
    fecha_registro_detalle.short_description = 'Registrado el'
    fecha_registro_detalle.admin_order_field = 'fecha_registro'
    readonly_fields = ('fecha_registro', 'dni_update_token', 'dni_email_sent_date')
    inlines = [MiembroGrupoInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel_view), name='api_asistente_import_excel'),
        ]
        return custom_urls + urls

    def import_excel_view(self, request):
        results = None
        
        # Validación de dependencia (Lazy Loading)
        try:
            import pandas as pd
        except ImportError:
            messages.error(request, "Error Crítico: El servidor no tiene instalada la librería 'pandas'. Por favor, contacta a soporte.")
            return render(request, 'admin/import_asistentes.html', {**self.admin_site.each_context(request), 'title': 'Carga Masiva (Error)'})

        if request.method == 'POST' and request.FILES.get('excel_file'):
            excel_file = request.FILES['excel_file']
            send_emails = request.POST.get('send_emails') == 'yes'
            
            try:
                # Leer archivo con pandas
                if excel_file.name.endswith('.csv'):
                    df = pd.read_csv(excel_file)
                else:
                    df = pd.read_excel(excel_file)
                
                # Normalizar nombres de columnas a minúsculas
                df.columns = [str(c).lower().strip() for c in df.columns]
                
                # Columnas requeridas
                required = ['nombre', 'apellido', 'email', 'dni']
                missing = [c for c in required if c not in df.columns]
                
                if missing:
                    messages.error(request, f"Faltan columnas obligatorias: {', '.join(missing)}")
                else:
                    edicion_activa = Edicion.objects.filter(activa=True).first()
                    if not edicion_activa:
                        messages.error(request, "No hay una edición activa configurada para vincular los registros.")
                    else:
                        stats = {'total': 0, 'created': 0, 'updated': 0, 'errors': 0, 'error_details': []}
                        
                        with transaction.atomic():
                            for index, row in df.iterrows():
                                stats['total'] += 1
                                try:
                                    dni = str(row.get('dni')).strip().split('.')[0] # Limpiar .0 de excels
                                    email = str(row.get('email')).strip().lower()
                                    nombre = str(row.get('nombre')).strip()
                                    apellido = str(row.get('apellido')).strip()
                                    
                                    if not dni or not email:
                                        raise ValueError("DNI o Email vacíos en la fila.")

                                    # 1. Crear/Actualizar Asistente
                                    profile_type = str(row.get('perfil', 'VISITOR')).upper().strip()
                                    # Mapear perfiles válidos
                                    if profile_type not in [t[0] for t in Asistente.ProfileType.choices]:
                                        profile_type = Asistente.ProfileType.VISITOR

                                    asistente, created = Asistente.objects.update_or_create(
                                        dni=dni,
                                        defaults={
                                            'first_name': nombre,
                                            'last_name': apellido,
                                            'email': email,
                                            'phone': str(row.get('telefono', '')).strip(),
                                            'profile_type': profile_type,
                                            'terminos_aceptados': True
                                        }
                                    )

                                    if created: stats['created'] += 1
                                    else: stats['updated'] += 1

                                    # 2. Vincular a Edición 2026 (Inscripcion)
                                    Inscripcion.objects.get_or_create(
                                        asistente=asistente,
                                        edicion=edicion_activa
                                    )

                                    # 3. Datos extra (Detalles)
                                    institucion = str(row.get('institucion', '')).strip()
                                    carrera_cargo = str(row.get('carrera', '')).strip()
                                    
                                    if institucion or carrera_cargo:
                                        from .models import DetalleEstudiante, DetalleDocente, DetalleProfesional
                                        if profile_type == Asistente.ProfileType.STUDENT:
                                            DetalleEstudiante.objects.update_or_create(asistente=asistente, defaults={'institution': institucion, 'career': carrera_cargo})
                                        elif profile_type == Asistente.ProfileType.TEACHER:
                                            DetalleDocente.objects.update_or_create(asistente=asistente, defaults={'institution': institucion, 'career_taught': carrera_cargo})
                                        elif profile_type == Asistente.ProfileType.PROFESSIONAL:
                                            DetalleProfesional.objects.update_or_create(asistente=asistente, defaults={'work_area': institucion, 'occupation': carrera_cargo})

                                    # 4. Enviar Email si se solicitó
                                    if send_emails:
                                        try:
                                            from .email import send_individual_confirmation_email
                                            send_individual_confirmation_email(asistente)
                                        except Exception as e:
                                            print(f"[ERROR] No se pudo enviar email en carga masiva a {asistente.email}: {e}")
                                            stats['error_details'].append({'row': index + 2, 'msg': f"Email fallido: {str(e)}"})

                                except Exception as e:
                                    stats['errors'] += 1
                                    stats['error_details'].append({'row': index + 2, 'msg': str(e)})
                        
                        results = stats
                        messages.success(request, f"Procesamiento masivo completado. {stats['created']} nuevos registros.")

            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {str(e)}")

        context = {
            **self.admin_site.each_context(request),
            'title': 'Carga Masiva de Asistentes',
            'results': results,
        }
        return render(request, 'admin/import_asistentes.html', context)
    
    def get_queryset(self, request):
        """
        Por defecto, muestra solo los registrados en la edición activa.
        Permite ver todos si se aplican filtros específicos.
        """
        qs = super().get_queryset(request)
        
        # Si no hay filtros de edición aplicados, filtrar por la activa por defecto
        if not request.GET.get('inscripciones__edicion__id__exact'):
            edicion_activa = Edicion.objects.filter(activa=True).first()
            if edicion_activa:
                qs = qs.filter(inscripciones__edicion=edicion_activa).distinct()
        
        return qs

    def get_ediciones(self, obj):
        ediciones = Edicion.objects.filter(inscripciones__asistente=obj).values_list('anio', flat=True)
        return ", ".join(map(str, ediciones)) if ediciones else "-"
    def get_asistencia_actual(self, obj):
        edicion_activa = Edicion.objects.filter(activa=True).first()
        if not edicion_activa: return "—"
        insc = obj.inscripciones.filter(edicion=edicion_activa).first()
        if insc and insc.asistencia_confirmada:
            return format_html('<span style="color: green;">✔ Confirmada</span>')
        return format_html('<span style="color: red;">✘ Pendiente</span>')
    get_asistencia_actual.short_description = 'Asistencia 2026'
    actions = ['confirmar_asistencia', 'enviar_certificados', 'enviar_solicitud_actualizacion_dni', 'enviar_certificados_lote_40', 'exportar_no_estudiantes_xls', 'exportar_asistentes_xls']
    def exportar_asistentes_xls(self, request, queryset):
        """
        Exporta todos los asistentes seleccionados a un archivo Excel (.xls)
        """
        import xlwt
        from django.http import HttpResponse

        asistentes = queryset
        if not asistentes.exists():
            self.message_user(request, "No hay asistentes en la selección.", level='warning')
            return

        wb = xlwt.Workbook()
        ws = wb.add_sheet('Asistentes')

        campos = [
            'first_name', 'last_name', 'email', 'dni', 'phone', 'profile_type',
            'rol_especifico', 'is_unab_student', 'institution', 'career', 'year_of_study',
            'career_taught', 'work_area', 'occupation', 'company_name', 'group_name',
            'group_municipality', 'group_size', 'asistencia_confirmada', 'fecha_confirmacion'
        ]
        for col, campo in enumerate(campos):
            ws.write(0, col, campo)

        # Obtener edición activa para los datos de asistencia
        edicion_activa = Edicion.objects.filter(activa=True).first()

        for row, asistente in enumerate(asistentes, start=1):
            # Obtener inscripción para la edición activa
            insc = asistente.inscripciones.filter(edicion=edicion_activa).first() if edicion_activa else None
            
            for col, campo in enumerate(campos):
                if campo == 'asistencia_confirmada':
                    valor = insc.asistencia_confirmada if insc else False
                elif campo == 'fecha_confirmacion':
                    valor = insc.fecha_confirmacion if insc else ''
                else:
                    valor = getattr(asistente, campo, '')
                
                ws.write(row, col, str(valor) if valor is not None else '')

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=asistentes.xls'
        wb.save(response)
        return response

    exportar_asistentes_xls.short_description = "Exportar asistentes seleccionados a Excel (.xls)"  # type: ignore

    def exportar_no_estudiantes_xls(self, request, queryset):
        """
        Exporta los asistentes seleccionados que NO son estudiantes a un archivo Excel (.xls)
        """
        import xlwt
        from django.http import HttpResponse

        # Filtrar solo los que no son estudiantes
        asistentes = queryset.exclude(profile_type='STUDENT')
        if not asistentes.exists():
            self.message_user(request, "No hay asistentes no estudiantes en la selección.", level='warning')
            return

        # Crear libro y hoja
        wb = xlwt.Workbook()
        ws = wb.add_sheet('No Estudiantes')

        # Definir campos a exportar
        campos = [
            'first_name', 'last_name', 'email', 'dni', 'phone', 'profile_type',
            'rol_especifico', 'is_unab_student', 'institution', 'career', 'year_of_study',
            'career_taught', 'work_area', 'occupation', 'company_name', 'group_name',
            'group_municipality', 'group_size', 'asistencia_confirmada', 'fecha_confirmacion'
        ]
        # Escribir cabeceras
        for col, campo in enumerate(campos):
            ws.write(0, col, campo)

        # Obtener edición activa
        edicion_activa = Edicion.objects.filter(activa=True).first()

        # Escribir datos
        for row, asistente in enumerate(asistentes, start=1):
            # Obtener inscripción para la edición activa
            insc = asistente.inscripciones.filter(edicion=edicion_activa).first() if edicion_activa else None

            for col, campo in enumerate(campos):
                if campo == 'asistencia_confirmada':
                    valor = insc.asistencia_confirmada if insc else False
                elif campo == 'fecha_confirmacion':
                    valor = insc.fecha_confirmacion if insc else ''
                else:
                    valor = getattr(asistente, campo, '')
                ws.write(row, col, str(valor) if valor is not None else '')

        # Preparar respuesta
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=asistentes_no_estudiantes.xls'
        wb.save(response)
        return response

    exportar_no_estudiantes_xls.short_description = "Exportar asistentes NO estudiantes a Excel (.xls)"  # type: ignore
    def enviar_certificados_lote_40(self, request, queryset):
        """
        Envía certificados solo a los asistentes seleccionados, confirmados el 15 de noviembre,
        en lotes de 40 para evitar errores de envío masivo.
        """
        from datetime import datetime, timedelta
        from django.utils import timezone
        # Fecha del evento: 15 de noviembre de 2025
        fecha_evento = datetime(2025, 11, 15, tzinfo=timezone.get_current_timezone())
        fecha_inicio = fecha_evento.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_evento.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Filtrar solo asistentes confirmados el 15 de noviembre
        asistentes = queryset.filter(
            asistencia_confirmada=True,
            fecha_confirmacion__range=(fecha_inicio, fecha_fin)
        )
        total = asistentes.count()
        if total == 0:
            self.message_user(request, "No hay asistentes confirmados el 15 de noviembre en la selección.", level='warning')
            return

        # Enviar en lotes de 40
        LOTE = 40
        enviados = 0
        errores = 0
        asistentes_lote = asistentes[:LOTE]
        for asistente in asistentes_lote:
            try:
                certificado, _ = Certificado.objects.get_or_create(
                    asistente=asistente,
                    tipo_certificado=Certificado.TipoCertificado.ASISTENCIA
                )
                send_certificate_email(certificado)
                enviados += 1
            except Exception as e:
                errores += 1
        mensaje = f"Se enviaron {enviados} certificados en este lote."
        if errores:
            mensaje += f" Hubo {errores} errores."
        if total > LOTE:
            mensaje += f" Quedan {total - LOTE} asistentes pendientes. Ejecuta la acción nuevamente para continuar."
        self.message_user(request, mensaje)

    enviar_certificados_lote_40.short_description = "Enviar certificados (confirmados 15/11, lote de 40)"  # type: ignore

    def enviar_solicitud_actualizacion_dni(self, request, queryset):
        """
        Envía email a los asistentes seleccionados que no tienen DNI válido,
        con un enlace para que actualicen su DNI.
        
        LÍMITE: Máximo 50 correos por ejecución para evitar timeouts.
        Solo envía a quienes NO han recibido el correo previamente.
        """
        # Filtrar solo asistentes sin DNI válido (con token asignado) Y que no hayan recibido el correo
        asistentes_sin_dni = queryset.filter(
            models.Q(dni__isnull=True) | models.Q(dni=''),
            dni_email_sent=False  # Solo quienes NO han recibido el correo
        )
        
        if not asistentes_sin_dni.exists():
            # Verificar si hay asistentes que ya recibieron el correo
            ya_enviados = queryset.filter(
                models.Q(dni__isnull=True) | models.Q(dni=''),
                dni_email_sent=True
            ).count()
            
            if ya_enviados > 0:
                self.message_user(
                    request, 
                    f"✅ Los {ya_enviados} asistentes seleccionados ya recibieron el correo de solicitud de DNI.",
                    level='info'
                )
            else:
                self.message_user(request, "Los asistentes seleccionados ya tienen DNI válido.", level='warning')
            return
        
        # LIMITAR a 50 para evitar timeout de Gunicorn
        MAX_EMAILS = 50
        total_sin_dni = asistentes_sin_dni.count()
        asistentes_lote = asistentes_sin_dni[:MAX_EMAILS]
        
        if total_sin_dni > MAX_EMAILS:
            self.message_user(
                request, 
                f"⚠️ Hay {total_sin_dni} asistentes sin DNI que no han recibido el correo. "
                f"Solo se enviarán {MAX_EMAILS} correos en este lote. "
                f"Ejecuta la acción nuevamente para enviar los siguientes.",
                level='warning'
            )
        
        enviados = 0
        errores = 0
        sin_token = 0
        
        for asistente in asistentes_lote:
            if not asistente.dni_update_token:
                sin_token += 1
                continue
            
            try:
                # Construir el enlace
                base_url = getattr(settings, 'FRONTEND_URL', 'https://congresologistica.unab.edu.ar')
                enlace = f"{base_url}/actualizar-dni?token={asistente.dni_update_token}"
                
                # Renderizar el template
                html_content = render_to_string('email/dni_update.html', {
                    'nombre': asistente.first_name,
                    'enlace': enlace
                })
                
                # Crear y enviar el email
                subject = 'Actualización de DNI - Congreso de Logística UNaB 2025'
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = asistente.email
                
                email = EmailMultiAlternatives(subject, '', from_email, [to_email])
                email.attach_alternative(html_content, "text/html")
                email.send()
                
                # MARCAR como enviado
                asistente.dni_email_sent = True
                asistente.dni_email_sent_date = timezone.now()
                asistente.save(update_fields=['dni_email_sent', 'dni_email_sent_date'])
                
                enviados += 1
            except Exception as e:
                errores += 1
                print(f"[ERROR] Error enviando email a {asistente.email}: {e}")
        
        # Mensaje final con resumen
        mensaje = f"✅ {enviados} emails enviados correctamente."
        if errores > 0:
            mensaje += f" ❌ {errores} errores."
        if sin_token > 0:
            mensaje += f" ⚠️ {sin_token} sin token (ejecuta fix_dni.py)."
        if total_sin_dni > MAX_EMAILS:
            pendientes = total_sin_dni - MAX_EMAILS
            mensaje += f" 📬 Quedan {pendientes} pendientes de enviar."
        
        self.message_user(request, mensaje)
    
    enviar_solicitud_actualizacion_dni.short_description = "Enviar solicitud de actualización de DNI (máx. 50)"  # type: ignore

    def confirmar_asistencia(self, request, queryset):
        edicion_activa = Edicion.objects.filter(activa=True).first()
        if not edicion_activa:
            self.message_user(request, "No hay una edición activa configurada.", level='error')
            return

        updated_count = 0
        for asistente in queryset:
            insc, created = Inscripcion.objects.get_or_create(asistente=asistente, edicion=edicion_activa)
            if not insc.asistencia_confirmada:
                insc.asistencia_confirmada = True
                insc.fecha_confirmacion = timezone.now()
                insc.save()
                
                # Crear certificado de asistencia
                Certificado.objects.get_or_create(
                    asistente=asistente,
                    tipo_certificado=Certificado.TipoCertificado.ASISTENCIA
                )
                updated_count += 1
        
        self.message_user(request, f"{updated_count} asistencias confirmadas para {edicion_activa}. Los certificados están en cola.")
    confirmar_asistencia.short_description = "Confirmar asistencia edición activa (Cola certificados)"  # type: ignore

    def enviar_certificados(self, request, queryset):
        edicion_activa = Edicion.objects.filter(activa=True).first()
        queued_count = 0
        for asistente in queryset:
            insc = Inscripcion.objects.filter(asistente=asistente, edicion=edicion_activa, asistencia_confirmada=True).first()
            if insc:
                obj, created = Certificado.objects.get_or_create(
                    asistente=asistente,
                    tipo_certificado=Certificado.TipoCertificado.ASISTENCIA
                )
                if created or not obj.email_enviado:
                    queued_count += 1
        
        self.message_user(request, f"{queued_count} certificados listos en la cola para ser procesados.")
    enviar_certificados.short_description = "Añadir certificados de seleccionados a la cola"  # type: ignore

class CertificadoAdmin(admin.ModelAdmin):
    list_display = ('asistente', 'tipo_certificado', 'email_enviado', 'fecha_envio', 'intentos', 'fecha_generacion')
    list_filter = ('tipo_certificado', 'email_enviado', 'fecha_generacion')
    search_fields = ('asistente__first_name', 'asistente__last_name', 'asistente__email')
    readonly_fields = ('fecha_generacion', 'fecha_envio', 'intentos')
    actions = ['enviar_por_email_accion_masiva']

    def enviar_por_email_accion_masiva(self, request, queryset):
        # Redirigir a la nueva interfaz de procesamiento por lotes si es necesario, 
        # o simplemente marcar para re-intento.
        queryset.update(email_enviado=False, intentos=0)
        self.message_user(request, f"{queryset.count()} certificados reiniciados para re-envío en la cola.")
    enviar_por_email_accion_masiva.short_description = "Reiniciar envío para seleccionados (Volver a cola)"

    def enviar_por_email_accion(self, request, queryset):
        sent_count = 0
        errores = 0
        for certificado in queryset:
            try:
                send_certificate_email(certificado)
                sent_count += 1
            except Exception:
                errores += 1
        
        msg = f"{sent_count} certificados enviados."
        if errores:
            msg += f" {errores} errores detectados."
            self.message_user(request, msg, level='warning')
        else:
            self.message_user(request, msg)
    enviar_por_email_accion.short_description = "Re-enviar certificados seleccionados por Email" # type: ignore

class ProgramaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'aula', 'dia', 'hora_inicio', 'hora_fin', 'edicion')
    list_filter = ('edicion', 'dia', 'categoria', 'aula')
    search_fields = ('titulo',)
    list_editable = ('categoria',)
    
    actions = ['set_logistica', 'set_tecnologia']

    def set_logistica(self, request, queryset):
        queryset.update(categoria='LOGISTICA')
    set_logistica.short_description = "Cambiar categoría a Logística" # type: ignore

    def set_tecnologia(self, request, queryset):
        queryset.update(categoria='TECNOLOGIA')
    set_tecnologia.short_description = "Cambiar categoría a Tecnología" # type: ignore

@admin.register(Disertante)
class DisertanteAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('nombre', 'foto', 'foto_url', 'tema_presentacion', 'linkedin')
        }),
        ('Información opcional', {
            'classes': ('collapse',),
            'fields': ('bio',),
        }),
    )
    list_display = ('nombre', 'tema_presentacion', 'edicion', 'linkedin')
    list_filter = ('edicion', 'estado')
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'estado', 'edicion', 'numero_stand', 'cantidad_representantes', 'fecha_registro')
    list_filter = ('estado', 'edicion', 'participo_edicion_anterior')
    search_fields = ('nombre_empresa', 'cuit', 'email_contacto', 'nombre_contacto')
    list_editable = ('estado', 'numero_stand', 'cantidad_representantes')
    actions = ['aprobar_empresas', 'rechazar_empresas']
    readonly_fields = ('fecha_registro', 'fecha_revision', 'revisada_por')
    fieldsets = (
        ('Identificación', {
            'fields': ('edicion', 'estado', 'nombre_empresa', 'logo', 'cuit', 'descripcion')
        }),
        ('Contacto', {
            'fields': ('nombre_contacto', 'email_contacto', 'celular_contacto', 'cargo_contacto',
                       'telefono_empresa', 'email_empresa', 'sitio_web', 'direccion')
        }),
        ('Participación', {
            'fields': ('participacion_opciones', 'participacion_otra', 'rubro_logistico',
                       'participo_edicion_anterior', 'acepta_tyc')
        }),
        ('Logística del Stand', {
            'classes': ('collapse',),
            'fields': ('numero_stand', 'cantidad_representantes', 'requiere_electricidad',
                       'computadora_o_pantalla', 'tipo_mobiliario', 'gazebo_propio',
                       'estructura_adicional', 'acciones_stand')
        }),
        ('Gestión Interna (solo admin)', {
            'classes': ('collapse',),
            'fields': ('notas_admin', 'fecha_revision', 'revisada_por')
        }),
    )

    def save_model(self, request, obj, form, change):
        if 'estado' in form.changed_data:
            obj.fecha_revision = timezone.now()
            obj.revisada_por = request.user
        super().save_model(request, obj, form, change)

    def aprobar_empresas(self, request, queryset):
        updated = queryset.update(estado='APROBADO', fecha_revision=timezone.now(), revisada_por=request.user)
        self.message_user(request, f'{updated} empresa(s) aprobada(s).')
    aprobar_empresas.short_description = 'Aprobar empresas seleccionadas'  # type: ignore

    def rechazar_empresas(self, request, queryset):
        updated = queryset.update(estado='RECHAZADO', fecha_revision=timezone.now(), revisada_por=request.user)
        self.message_user(request, f'{updated} empresa(s) rechazada(s).')
    rechazar_empresas.short_description = 'Rechazar empresas seleccionadas'  # type: ignore


@admin.register(PostulacionDisertante)
class PostulacionDisertanteAdmin(admin.ModelAdmin):
    list_display = ('nombre_apellido', 'email', 'titulo_charla', 'estado', 'edicion', 'fecha_postulacion')
    list_filter = ('estado', 'edicion', 'modalidad')
    search_fields = ('nombre_apellido', 'dni', 'email', 'titulo_charla')
    list_editable = ('estado',)
    actions = ['aprobar_postulaciones', 'rechazar_postulaciones']
    readonly_fields = ('fecha_postulacion', 'fecha_revision', 'revisada_por')
    fieldsets = (
        ('Datos personales', {
            'fields': ('edicion', 'nombre_apellido', 'dni', 'email', 'telefono',
                       'ciudad_provincia', 'profesion_cargo', 'empresa_institucion', 'linkedin', 'foto_perfil')
        }),
        ('Propuesta de charla', {
            'fields': ('titulo_charla', 'ejes_tematicos', 'eje_otro', 'resumen_charla',
                       'objetivos_charla', 'publico_dirigido', 'modalidad', 'participacion_tipo',
                       'duracion_estimada', 'requiere_equipamiento')
        }),
        ('Experiencia', {
            'classes': ('collapse',),
            'fields': ('experiencia_previa',)
        }),
        ('Estado y gestión', {
            'fields': ('estado', 'acepta_tyc', 'fecha_postulacion')
        }),
        ('Notas internas (solo admin)', {
            'classes': ('collapse',),
            'fields': ('notas_admin', 'fecha_revision', 'revisada_por')
        }),
    )

    def save_model(self, request, obj, form, change):
        if 'estado' in form.changed_data:
            obj.fecha_revision = timezone.now()
            obj.revisada_por = request.user
        super().save_model(request, obj, form, change)

    def aprobar_postulaciones(self, request, queryset):
        updated = queryset.update(estado='APROBADO', fecha_revision=timezone.now(), revisada_por=request.user)
        self.message_user(request, f'{updated} postulacion(es) de disertante aprobada(s).')
    aprobar_postulaciones.short_description = 'Aprobar postulaciones seleccionadas'  # type: ignore

    def rechazar_postulaciones(self, request, queryset):
        updated = queryset.update(estado='RECHAZADO', fecha_revision=timezone.now(), revisada_por=request.user)
        self.message_user(request, f'{updated} postulacion(es) de disertante rechazada(s).')
    rechazar_postulaciones.short_description = 'Rechazar postulaciones seleccionadas'  # type: ignore


@admin.register(InscripcionPrensa)
class InscripcionPrensaAdmin(admin.ModelAdmin):
    list_display = ('nombre_apellido', 'tipo_perfil', 'medio_o_canal', 'edicion', 'fecha_inscripcion', 'link_display')
    list_filter = ('tipo_perfil', 'edicion')
    search_fields = ('nombre_apellido', 'dni', 'email', 'medio_o_canal')
    readonly_fields = ('fecha_inscripcion',)
    fieldsets = (
        ('Datos personales', {
            'fields': ('edicion', 'nombre_apellido', 'dni', 'email', 'telefono', 'ciudad_provincia')
        }),
        ('Perfil mediático', {
            'fields': ('tipo_perfil', 'medio_o_canal', 'url_perfil_red', 'url_sitio_medio', 'seguidores_aprox')
        }),
        ('Administración', {
            'fields': ('acepta_tyc', 'fecha_inscripcion', 'notas_admin')
        }),
    )

    def link_display(self, obj):
        links = []
        if obj.url_perfil_red:
            links.append(format_html('<a href="{}" target="_blank">Red social</a>', obj.url_perfil_red))
        if obj.url_sitio_medio:
            links.append(format_html('<a href="{}" target="_blank">Sitio web</a>', obj.url_sitio_medio))
        return format_html(' | '.join(links)) if links else '—'
    link_display.short_description = 'Links'  # type: ignore
    link_display.allow_tags = True  # type: ignore


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('admin:admin-dashboard')

# Registros finales
admin.site.register(Asistente, AsistenteAdmin)
admin.site.register(Inscripcion, InscripcionAdmin)
admin.site.register(Certificado, CertificadoAdmin)
admin.site.register(Programa, ProgramaAdmin)
class EdicionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'anio', 'activa')
    list_editable = ('activa',)
    list_filter = ('activa',)
    actions = ['marcar_como_activa']

    def marcar_como_activa(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Seleccione solo una edición para activar.", level='warning')
            return
        edicion = queryset.first()
        edicion.activa = True
        edicion.save() # El método save ya se encarga de desactivar las otras
        self.message_user(request, f"La edición {edicion} ahora es la activa.")
    marcar_como_activa.short_description = "Marcar edición seleccionada como ACTIVA" # type: ignore

admin.site.register(Edicion, EdicionAdmin)

@admin.register(MiembroGrupo)
class MiembroGrupoAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'dni', 'representante', 'fecha_registro')
    list_filter = ('fecha_registro',)
    search_fields = ('full_name', 'dni', 'representante__first_name', 'representante__last_name')
    readonly_fields = ('fecha_registro',)