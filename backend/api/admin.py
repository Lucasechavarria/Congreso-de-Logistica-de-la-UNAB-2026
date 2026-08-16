from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
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
            destinatarios = request.POST.getlist('destinatarios')  # lista multi-valor
            asunto = request.POST.get('asunto')
            mensaje_html = request.POST.get('mensaje')

            if not destinatarios:
                messages.error(request, "Debés seleccionar al menos un grupo de destinatarios.")
            else:
                emails = set()

                # ── Asistentes ──────────────────────────────────────────────
                if 'ASISTENTES_TODOS' in destinatarios:
                    emails.update(Asistente.objects.values_list('email', flat=True))

                if 'ASISTENTES_CONFIRMADOS' in destinatarios:
                    from .models import Edicion
                    edicion_activa = Edicion.objects.filter(activa=True).first()
                    if edicion_activa:
                        emails.update(
                            Inscripcion.objects.filter(edicion=edicion_activa, asistencia_confirmada=True)
                            .values_list('asistente__email', flat=True)
                        )

                # ── Disertantes (por estado de postulación) ─────────────────
                if 'DISERTANTES_PENDIENTE' in destinatarios:
                    emails.update(PostulacionDisertante.objects.filter(estado='PENDIENTE').values_list('email', flat=True))

                if 'DISERTANTES_APROBADOS' in destinatarios:
                    emails.update(PostulacionDisertante.objects.filter(estado='APROBADO').values_list('email', flat=True))

                if 'DISERTANTES_RECHAZADOS' in destinatarios:
                    emails.update(PostulacionDisertante.objects.filter(estado='RECHAZADO').values_list('email', flat=True))

                # ── Prensa ──────────────────────────────────────────────────
                if 'PRENSA' in destinatarios:
                    emails.update(InscripcionPrensa.objects.values_list('email', flat=True))

                # ── Empresas (por estado del workflow) ──────────────────────
                EMPRESA_ESTADOS = {
                    'EMPRESAS_PENDIENTE':      'PENDIENTE',
                    'EMPRESAS_ENVIO_BC':       'ENVIO_BC',
                    'EMPRESAS_PENDIENTE_PAGO': 'PENDIENTE_PAGO',
                    'EMPRESAS_CONFIRMADAS':    'CONFIRMADA',
                    'EMPRESAS_RECHAZADAS':     'RECHAZADA',
                }
                for key, estado_val in EMPRESA_ESTADOS.items():
                    if key in destinatarios:
                        emails.update(
                            Empresa.objects.filter(estado=estado_val)
                            .exclude(email_contacto='').exclude(email_contacto__isnull=True)
                            .values_list('email_contacto', flat=True)
                        )

                # Limpiar emails vacíos y deduplicar
                emails_list = [e for e in emails if e]

                if not emails_list:
                    messages.error(request, "No se encontraron destinatarios para los grupos seleccionados.")
                else:
                    enviados, errores = send_broadcast_batch_email(emails_list, asunto, mensaje_html)
                    grupos_label = " · ".join(destinatarios)
                    msg = (
                        f"✅ Proceso finalizado. "
                        f"Destinatarios únicos: {len(emails_list)} | "
                        f"Enviados: {enviados} | Errores: {errores}. "
                        f"[{grupos_label}]"
                    )
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
    

def export_to_excel_action(modeladmin, request, queryset):
    """
    Acción global de Django Admin para exportar registros seleccionados/filtrados a Excel (.xlsx).
    Muestra cabeceras legibles en español y resuelve llaves foráneas a sus strings.
    """
    import io
    import pandas as pd
    from datetime import datetime
    from django.db import models
    from django.utils import timezone
    
    try:
        model = modeladmin.model
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"export_{model._meta.model_name}_{timestamp}.xlsx"
        
        # Optimizar consulta con select_related dinámico para llaves foráneas
        fk_fields = [f.name for f in model._meta.fields if isinstance(f, (models.ForeignKey, models.OneToOneField))]
        if fk_fields:
            queryset = queryset.select_related(*fk_fields)
            
        data = []
        for obj in queryset:
            row = {}
            for f in model._meta.fields:
                val = getattr(obj, f.name)
                header = str(f.verbose_name).capitalize()
                
                if val is None:
                    row[header] = ''
                elif isinstance(f, (models.ForeignKey, models.OneToOneField)):
                    row[header] = str(val)
                elif isinstance(f, (models.DateTimeField, models.DateField)):
                    if hasattr(val, 'tzinfo') and val is not None:
                        row[header] = val.astimezone(timezone.get_current_timezone()).replace(tzinfo=None)
                    else:
                        row[header] = val
                else:
                    row[header] = val
            data.append(row)
            
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=model._meta.object_name[:31], index=False)
            
        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        logger.error(f"Error en export_to_excel_action: {str(e)}", exc_info=True)
        messages.error(request, f"Error al exportar los datos a Excel: {str(e)}")
        return redirect(request.META.get('HTTP_REFERER', 'admin:index'))

export_to_excel_action.short_description = "📊 Exportar seleccionados a Excel (.xlsx)"


def backup_database_view(request):
    """
    Vista para descargar un backup completo de la base de datos en formato Excel (.xlsx).
    Exporta cada modelo gestionado de las aplicaciones 'api' y 'bolsa_trabajo' 
    en una pestaña individual. Solo accesible para superusers.
    """
    if not request.user.is_superuser:
        return HttpResponse("No autorizado.", status=403)
        
    import io
    import pandas as pd
    from datetime import datetime
    from django.apps import apps
    
    try:
        custom_apps = ['api', 'bolsa_trabajo']
        models_to_export = []
        
        for app_config in apps.get_app_configs():
            if app_config.label in custom_apps:
                for model in app_config.get_models():
                    if model._meta.managed:
                        models_to_export.append(model)
                        
        if not models_to_export:
            messages.warning(request, "No se encontraron modelos para exportar.")
            return redirect('admin:index')
            
        output = io.BytesIO()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_congreso_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for model in models_to_export:
                fields = [f.name for f in model._meta.fields]
                queryset = model.objects.all()
                data = list(queryset.values(*fields))
                
                df = pd.DataFrame(data, columns=fields)
                
                for col in df.columns:
                    if isinstance(df[col].dtype, pd.DatetimeTZDtype):
                        df[col] = df[col].dt.tz_localize(None)
                    elif df[col].dtype == 'object':
                        df[col] = df[col].apply(lambda x: x.replace(tzinfo=None) if hasattr(x, 'tzinfo') and x is not None else x)
                
                sheet_name = model._meta.object_name[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        logger.error(f"Error en backup_database_view (.xlsx): {str(e)}", exc_info=True)
        messages.error(request, f"Error generando backup en Excel: {str(e)}")
        return redirect('admin:index')


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
            result = send_certificate_email(cert)
            success = result[0] if isinstance(result, tuple) else result
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


@admin.site.admin_view
def dashboard_api_view(request):
    """
    Endpoint JSON para procesar y retornar estadísticas de segmentos analíticos 
    personalizados construidos por el usuario de forma dinámica y segura.
    """
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)
        
    import json
    
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
        else:
            data = json.loads(request.GET.get('data', '{}'))
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'JSON inválido: {str(e)}'}, status=400)
        
    periodo = data.get('periodo', 'diario')
    alineacion = data.get('alineacion', 'campania')
    edicion_sel_id = data.get('edicion')
    segmentos = data.get('segmentos', [])
    
    # Determinar truncado temporal
    if periodo == 'semanal':
        trunc_func = TruncWeek
    elif periodo == 'mensual':
        trunc_func = TruncMonth
    else:
        trunc_func = TruncDate
        
    series_response = []
    
    for seg in segmentos:
        nombre = seg.get('nombre', 'Segmento')
        entidad = seg.get('entidad', 'asistentes')
        combinador = seg.get('combinador', 'AND')
        reglas = seg.get('reglas', [])
        
        # QuerySet Base Optimizado para evitar N+1 en DB
        if entidad == 'empresas':
            qs = Empresa.objects.all().select_related('edicion')
            date_field = 'fecha_registro'
        elif entidad == 'disertantes':
            qs = PostulacionDisertante.objects.all().select_related('edicion')
            date_field = 'fecha_postulacion'
        else:
            qs = Asistente.objects.all().select_related(
                'detalle_estudiante', 'detalle_docente', 'detalle_profesional', 'detalle_grupo'
            ).prefetch_related('inscripciones')
            date_field = 'fecha_registro'
            
        # Solo filtrar por edición global si el segmento NO define una regla de edición específica
        has_seg_edicion = any(r.get('campo') == 'edicion' for r in reglas)
        if edicion_sel_id and edicion_sel_id != 'todas' and not has_seg_edicion:
            try:
                ed_id = int(edicion_sel_id)
                if entidad == 'empresas':
                    qs = qs.filter(edicion_id=ed_id)
                elif entidad == 'disertantes':
                    qs = qs.filter(edicion_id=ed_id)
                else:
                    qs = qs.filter(inscripciones__edicion_id=ed_id)
            except ValueError:
                pass
                
        # Construir consulta dinámica y segura mediante Q-objects
        segment_q = models.Q()
        
        for r in reglas:
            campo = r.get('campo')
            operador = r.get('operador', 'exact')
            valor = r.get('valor')
            
            if not campo or valor is None:
                continue
                
            q_rule = models.Q()
            
            if campo == 'profile_type':
                q_rule = models.Q(profile_type=valor)
            elif campo == 'pertenece_unab':
                unab_q = (
                    models.Q(detalle_estudiante__is_unab_student=True) |
                    models.Q(detalle_estudiante__institution__icontains='unab') |
                    models.Q(detalle_estudiante__institution__icontains='almirante brown') |
                    models.Q(detalle_docente__institution__icontains='unab') |
                    models.Q(detalle_docente__institution__icontains='almirante brown')
                )
                q_rule = unab_q if valor == 'si' else ~unab_q
            elif campo == 'asistencia_confirmada':
                confirm_q = models.Q(inscripciones__asistencia_confirmada=True)
                if edicion_sel_id and edicion_sel_id != 'todas':
                    confirm_q &= models.Q(inscripciones__edicion_id=edicion_sel_id)
                q_rule = confirm_q if valor == 'si' else ~confirm_q
            elif campo == 'has_dni':
                dni_q = models.Q(dni__isnull=False) & ~models.Q(dni='')
                q_rule = dni_q if valor == 'si' else ~dni_q
            elif campo == 'institucion':
                if operador == 'contains':
                    q_rule = (
                        models.Q(detalle_estudiante__institution__icontains=valor) |
                        models.Q(detalle_docente__institution__icontains=valor) |
                        models.Q(detalle_grupo__institution_or_workplace__icontains=valor)
                    )
                else:
                    q_rule = (
                        models.Q(detalle_estudiante__institution=valor) |
                        models.Q(detalle_docente__institution=valor) |
                        models.Q(detalle_grupo__institution_or_workplace=valor)
                    )
            elif campo == 'carrera':
                if operador == 'contains':
                    q_rule = (
                        models.Q(detalle_estudiante__career__icontains=valor) |
                        models.Q(detalle_docente__career_taught__icontains=valor) |
                        models.Q(detalle_profesional__occupation__icontains=valor)
                    )
                else:
                    q_rule = (
                        models.Q(detalle_estudiante__career=valor) |
                        models.Q(detalle_docente__career_taught=valor) |
                        models.Q(detalle_profesional__occupation=valor)
                    )
            elif campo == 'comision':
                q_rule = models.Q(comision__icontains=valor) if operador == 'contains' else models.Q(comision=valor)
            elif campo == 'year_of_study':
                try:
                    q_rule = models.Q(detalle_estudiante__year_of_study=int(valor))
                except ValueError:
                    pass
            elif campo == 'work_area':
                q_rule = models.Q(detalle_profesional__work_area__icontains=valor) if operador == 'contains' else models.Q(detalle_profesional__work_area=valor)
            elif campo == 'group_name':
                q_rule = models.Q(detalle_grupo__group_name__icontains=valor) if operador == 'contains' else models.Q(detalle_grupo__group_name=valor)
            elif campo == 'group_municipality':
                q_rule = models.Q(detalle_grupo__group_municipality__icontains=valor) if operador == 'contains' else models.Q(detalle_grupo__group_municipality=valor)
            elif campo == 'tipo_grupo':
                q_rule = models.Q(detalle_grupo__tipo_grupo__icontains=valor)
            
            # Campos de Empresa
            elif campo == 'estado':
                q_rule = models.Q(estado=valor)
            elif campo == 'es_sponsor':
                q_rule = models.Q(es_sponsor=(valor == 'si' or valor is True))
            elif campo == 'participo_edicion_anterior':
                q_rule = models.Q(participo_edicion_anterior=(valor == 'si' or valor is True))
            elif campo == 'requiere_electricidad':
                q_rule = models.Q(requiere_electricidad=(valor == 'si' or valor is True))
            elif campo == 'computadora_o_pantalla':
                q_rule = models.Q(computadora_o_pantalla=(valor == 'si' or valor is True))
            elif campo == 'gazebo_propio':
                q_rule = models.Q(gazebo_propio=(valor == 'si' or valor is True))
            elif campo == 'rubro_logistico':
                q_rule = models.Q(rubro_logistico__icontains=valor) if operador == 'contains' else models.Q(rubro_logistico=valor)
            elif campo == 'tipo_mobiliario':
                q_rule = models.Q(tipo_mobiliario=valor)
                
            # Campos de PostulacionDisertante
            elif campo == 'modalidad':
                q_rule = models.Q(modalidad__icontains=valor) if operador == 'contains' else models.Q(modalidad=valor)
            elif campo == 'profesion_cargo':
                q_rule = models.Q(profesion_cargo__icontains=valor) if operador == 'contains' else models.Q(profesion_cargo=valor)
            elif campo == 'empresa_institucion':
                q_rule = models.Q(empresa_institucion__icontains=valor) if operador == 'contains' else models.Q(empresa_institucion=valor)
            elif campo == 'ejes_tematicos':
                q_rule = models.Q(ejes_tematicos__icontains=valor)
            elif campo == 'participacion_tipo':
                q_rule = models.Q(participacion_tipo__icontains=valor)
            elif campo == 'requiere_equipamiento':
                q_rule = models.Q(requiere_equipamiento__icontains=valor) if operador == 'contains' else models.Q(requiere_equipamiento=valor)
                
            # Filtro de Edición por Segmento (Comparativas Cruzadas)
            elif campo == 'edicion':
                try:
                    anio_val = int(valor)
                    if entidad == 'empresas' or entidad == 'disertantes':
                        q_rule = models.Q(edicion__anio=anio_val)
                    else:
                        q_rule = models.Q(inscripciones__edicion__anio=anio_val)
                except ValueError:
                    pass
                
            # Combinar lógica
            if segment_q:
                if combinador == 'OR':
                    segment_q |= q_rule
                else:
                    segment_q &= q_rule
            else:
                segment_q = q_rule
                
        if segment_q:
            qs = qs.filter(segment_q).distinct()
            
        # Agrupación y cuenta
        # Evitar errores si no hay registros
        stats_query = qs.annotate(period=trunc_func(date_field))
        raw_data = stats_query.values('period').annotate(count=Count('id', distinct=True)).order_by('period')
        
        points = []
        cumulative = 0
        for item in raw_data:
            if not item['period']:
                continue
            cumulative += item['count']
            date_str = item['period'].strftime('%Y-%m-%d')
            points.append({
                'date': date_str,
                'count': item['count'],
                'cumulative': cumulative
            })
            
        # Alineación temporal avanzada
        if alineacion == 'campania' and points:
            primer_dia = timezone.datetime.strptime(points[0]['date'], '%Y-%m-%d').date()
            for p in points:
                cur_dia = timezone.datetime.strptime(p['date'], '%Y-%m-%d').date()
                p['aligned_day'] = (cur_dia - primer_dia).days + 1
        elif alineacion == 'cuenta_regresiva' and points and edicion_sel_id and edicion_sel_id != 'todas':
            fecha_evento = None
            try:
                first_prog = Programa.objects.filter(edicion_id=edicion_sel_id).order_by('dia').first()
                if first_prog:
                    fecha_evento = first_prog.dia
            except Exception:
                pass
            if not fecha_evento:
                try:
                    ed = Edicion.objects.get(id=edicion_sel_id)
                    fecha_evento = timezone.datetime(ed.anio, 11, 15).date()
                except Exception:
                    fecha_evento = timezone.now().date()
                    
            for p in points:
                cur_dia = timezone.datetime.strptime(p['date'], '%Y-%m-%d').date()
                p['aligned_day'] = (cur_dia - fecha_evento).days
                
        series_response.append({
            'segment_name': nombre,
            'points': points
        })
        
    return JsonResponse({
        'status': 'success',
        'series': series_response
    })


# Inyectar el dashboard en el Admin de Django
def patch_admin_urls():
    original_get_urls = admin.site.get_urls
    
    def get_urls(*args, **kwargs):
        urls = original_get_urls(*args, **kwargs)
        custom_urls = [
            path('dashboard/', admin.site.admin_view(admin_dashboard), name='admin-dashboard'),
            path('dashboard-api/', admin.site.admin_view(dashboard_api_view), name='admin-dashboard-api'),
            path('broadcast/', admin.site.admin_view(broadcast_view), name='admin-broadcast'),
            path('backup-db/', admin.site.admin_view(backup_database_view), name='admin-backup-db'),
            path('certificate-queue/', admin.site.admin_view(certificate_queue_view), name='admin-certificate-queue'),
            path('process-certificate-batch/', admin.site.admin_view(process_certificate_batch_api), name='process-certificate-batch'),
            path('manual-certificate/', admin.site.admin_view(manual_certificate_view), name='admin-manual-certificate'),
            path('asistentes-search/', admin.site.admin_view(asistentes_search_api), name='admin-asistentes-search'),
        ]
        return custom_urls + urls
    
    admin.site.get_urls = get_urls
    
patch_admin_urls()
admin.site.add_action(export_to_excel_action)

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
        if self.value():
            valores = self.value().split(',')
            if len(valores) > 1:
                return queryset
            val = valores[0]
            if val == 'sin_dni':
                return queryset.filter(dni__isnull=True) | queryset.filter(dni='')
            if val == 'con_dni':
                return queryset.exclude(dni__isnull=True).exclude(dni='')
        return queryset


class InstitucionFilter(admin.SimpleListFilter):
    title = 'Institución'
    parameter_name = 'institucion'

    def lookups(self, request, model_admin):
        from .models import DetalleEstudiante, DetalleDocente, DetalleGrupo
        
        inst_estudiantes = DetalleEstudiante.objects.exclude(institution='').exclude(institution__isnull=True).values_list('institution', flat=True).distinct()
        inst_docentes = DetalleDocente.objects.exclude(institution='').exclude(institution__isnull=True).values_list('institution', flat=True).distinct()
        inst_grupos = DetalleGrupo.objects.exclude(institution_or_workplace='').exclude(institution_or_workplace__isnull=True).values_list('institution_or_workplace', flat=True).distinct()
        
        todas = set()
        for inst in list(inst_estudiantes) + list(inst_docentes) + list(inst_grupos):
            clean_inst = inst.strip()
            if clean_inst:
                todas.add(clean_inst)
                
        return sorted([(i, i) for i in todas], key=lambda x: x[1].lower())

    def queryset(self, request, queryset):
        if self.value():
            valores = self.value().split(',')
            q_obj = models.Q()
            for val in valores:
                q_obj |= (
                    models.Q(detalle_estudiante__institution=val) |
                    models.Q(detalle_docente__institution=val) |
                    models.Q(detalle_grupo__institution_or_workplace=val)
                )
            return queryset.filter(q_obj).distinct()
        return queryset


class CarreraFilter(admin.SimpleListFilter):
    title = 'Carrera / Cargo'
    parameter_name = 'carrera'

    def lookups(self, request, model_admin):
        from .models import DetalleEstudiante, DetalleDocente, DetalleProfesional
        
        carreras_est = DetalleEstudiante.objects.exclude(career='').exclude(career__isnull=True).values_list('career', flat=True).distinct()
        carreras_doc = DetalleDocente.objects.exclude(career_taught='').exclude(career_taught__isnull=True).values_list('career_taught', flat=True).distinct()
        cargos_prof = DetalleProfesional.objects.exclude(occupation='').exclude(occupation__isnull=True).values_list('occupation', flat=True).distinct()
        
        todas = set()
        for carr in list(carreras_est) + list(carreras_doc) + list(cargos_prof):
            clean_carr = carr.strip()
            if clean_carr:
                todas.add(clean_carr)
                
        return sorted([(c, c) for c in todas], key=lambda x: x[1].lower())

    def queryset(self, request, queryset):
        if self.value():
            valores = self.value().split(',')
            q_obj = models.Q()
            for val in valores:
                q_obj |= (
                    models.Q(detalle_estudiante__career=val) |
                    models.Q(detalle_docente__career_taught=val) |
                    models.Q(detalle_profesional__occupation=val)
                )
            return queryset.filter(q_obj).distinct()
        return queryset


class EsUNaBFilter(admin.SimpleListFilter):
    title = 'Pertenencia UNaB'
    parameter_name = 'pertenece_unab'

    def lookups(self, request, model_admin):
        return [
            ('si', 'Sí (Estudiante o Docente UNaB)'),
            ('no', 'No (Externo / Particular)'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            valores = self.value().split(',')
            if len(valores) > 1:
                return queryset
            val = valores[0]
            if val == 'si':
                return queryset.filter(
                    models.Q(detalle_estudiante__is_unab_student=True) |
                    models.Q(detalle_estudiante__institution__icontains='unab') |
                    models.Q(detalle_estudiante__institution__icontains='almirante brown') |
                    models.Q(detalle_docente__institution__icontains='unab') |
                    models.Q(detalle_docente__institution__icontains='almirante brown')
                ).distinct()
            if val == 'no':
                return queryset.exclude(
                    models.Q(detalle_estudiante__is_unab_student=True) |
                    models.Q(detalle_estudiante__institution__icontains='unab') |
                    models.Q(detalle_estudiante__institution__icontains='almirante brown') |
                    models.Q(detalle_docente__institution__icontains='unab') |
                    models.Q(detalle_docente__institution__icontains='almirante brown')
                ).distinct()
        return queryset


class AsistenciaEdicionActivaFilter(admin.SimpleListFilter):
    title = 'Asistencia (Edición Activa)'
    parameter_name = 'asistencia_activa'

    def lookups(self, request, model_admin):
        return [
            ('confirmado', '✔ Confirmada'),
            ('pendiente', '✘ Pendiente'),
        ]

    def queryset(self, request, queryset):
        from .models import Edicion
        edicion_activa = Edicion.objects.filter(activa=True).first()
        if not edicion_activa:
            return queryset
            
        if self.value():
            valores = self.value().split(',')
            if len(valores) > 1:
                return queryset
            val = valores[0]
            if val == 'confirmado':
                return queryset.filter(inscripciones__edicion=edicion_activa, inscripciones__asistencia_confirmada=True).distinct()
            if val == 'pendiente':
                confirmados = queryset.filter(inscripciones__edicion=edicion_activa, inscripciones__asistencia_confirmada=True).values_list('id', flat=True)
                return queryset.filter(inscripciones__edicion=edicion_activa).exclude(id__in=confirmados).distinct()
        return queryset



class MiembroGrupoInline(admin.TabularInline):
    model = MiembroGrupo
    extra = 0
    readonly_fields = ('fecha_registro',)

def asistentes_search_api(request):
    """
    Endpoint AJAX para buscar asistentes por nombre, apellido, email o DNI.
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
        
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
        
    asistentes = Asistente.objects.filter(
        models.Q(first_name__icontains=q) |
        models.Q(last_name__icontains=q) |
        models.Q(email__icontains=q) |
        models.Q(dni__icontains=q)
    ).distinct()[:15]
    
    results = []
    for a in asistentes:
        results.append({
            'id': a.id,
            'nombre': f"{a.first_name} {a.last_name}".strip(),
            'email': a.email,
            'dni': a.dni or '',
            'perfil': a.get_profile_type_display() if hasattr(a, 'get_profile_type_display') else a.profile_type
        })
        
    return JsonResponse({'results': results})


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

class InscripcionAdmin(SimpleHistoryAdmin):
    list_display = ('asistente', 'empresa', 'fecha_inscripcion_detalle', 'edicion')
    list_filter = ('edicion', 'fecha_inscripcion')
    search_fields = ('asistente__first_name', 'asistente__last_name', 'asistente__email', 'empresa__nombre_empresa')
    readonly_fields = ('fecha_inscripcion',)
    ordering = ['-fecha_inscripcion']

    def fecha_inscripcion_detalle(self, obj):
        return obj.fecha_inscripcion.strftime("%d/%m/%Y %H:%M:%S") if obj.fecha_inscripcion else "-"
    fecha_inscripcion_detalle.short_description = 'Fecha Inscripción'
    fecha_inscripcion_detalle.admin_order_field = 'fecha_inscripcion'

class AsistenteAdmin(SimpleHistoryAdmin):
    class Media:
        js = ('admin/js/multiselect_filters.js',)

    list_display = ('first_name', 'last_name', 'email', 'perfil_badge', 'dni', 'get_ediciones', 'get_asistencia_actual', 'fecha_registro_detalle')
    list_filter = (
        'profile_type',
        EsUNaBFilter,
        InstitucionFilter,
        CarreraFilter,
        'comision',
        DNIFilter,
        AsistenciaEdicionActivaFilter,
        'inscripciones__edicion',
        'fecha_registro'
    )
    search_fields = (
        'first_name',
        'last_name',
        'email',
        'dni',
        'comision',
        'detalle_estudiante__institution',
        'detalle_docente__institution',
        'detalle_estudiante__career',
        'detalle_docente__career_taught',
        'detalle_profesional__occupation'
    )
    ordering = ['-fecha_registro']

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
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'status': 'error', 'message': "Error Crítico: El servidor no tiene instalada la librería 'pandas'."})
            messages.error(request, "Error Crítico: El servidor no tiene instalada la librería 'pandas'. Por favor, contacta a soporte.")
            return render(request, 'admin/import_asistentes.html', {**self.admin_site.each_context(request), 'title': 'Carga Masiva (Error)'})

        # 1. Manejo de POST AJAX para Procesamiento Fila por Fila (JSON)
        if request.method == 'POST' and request.content_type == 'application/json':
            try:
                import json
                data = json.loads(request.body)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f"JSON inválido: {str(e)}"})

            action = data.get('action')
            if action == 'import_row':
                edicion_activa = Edicion.objects.filter(activa=True).first()
                if not edicion_activa:
                    return JsonResponse({'status': 'error', 'message': "No hay una edición activa configurada para vincular los registros."})

                row_data = data.get('row', {})
                dni = str(row_data.get('dni', '')).strip().split('.')[0]
                email = str(row_data.get('email', '')).strip().lower()
                nombre = str(row_data.get('nombre', '')).strip()
                apellido = str(row_data.get('apellido', '')).strip()
                telefono = str(row_data.get('telefono', '')).strip()
                profile_type = str(row_data.get('perfil', 'VISITOR')).upper().strip()
                institucion = str(row_data.get('institucion', '')).strip()
                carrera_cargo = str(row_data.get('carrera', '')).strip()
                comision_excel = str(row_data.get('comision', '')).strip()
                send_emails = data.get('send_emails', False)

                if not dni or not email or not nombre or not apellido:
                    missing = []
                    if not dni: missing.append("DNI")
                    if not email: missing.append("Email")
                    if not nombre: missing.append("Nombre")
                    if not apellido: missing.append("Apellido")
                    return JsonResponse({'status': 'error', 'message': f"Datos básicos faltantes: {', '.join(missing)}"})

                if profile_type not in [t[0] for t in Asistente.ProfileType.choices]:
                    profile_type = Asistente.ProfileType.VISITOR

                try:
                    with transaction.atomic():
                        asistente, created = Asistente.objects.update_or_create(
                            dni=dni,
                            defaults={
                                'first_name': nombre,
                                'last_name': apellido,
                                'email': email,
                                'phone': telefono,
                                'profile_type': profile_type,
                                'terminos_aceptados': True
                            }
                        )

                        action_taken = "created" if created else "updated"

                        # Vincular a edición activa
                        Inscripcion.objects.get_or_create(
                            asistente=asistente,
                            edicion=edicion_activa
                        )

                        # Datos extra (Detalles)
                        if comision_excel:
                            asistente.comision = comision_excel
                            asistente.save()
                        
                        if institucion or carrera_cargo:
                            from .models import DetalleEstudiante, DetalleDocente, DetalleProfesional
                            if profile_type in [Asistente.ProfileType.STUDENT, Asistente.ProfileType.GRADUADO]:
                                DetalleEstudiante.objects.update_or_create(asistente=asistente, defaults={'institution': institucion, 'career': carrera_cargo})
                            elif profile_type == Asistente.ProfileType.TEACHER:
                                DetalleDocente.objects.update_or_create(asistente=asistente, defaults={'institution': institucion, 'career_taught': carrera_cargo})
                            elif profile_type in [Asistente.ProfileType.PROFESSIONAL, Asistente.ProfileType.OTRO]:
                                work_area = institucion if profile_type == Asistente.ProfileType.PROFESSIONAL else "Otro"
                                DetalleProfesional.objects.update_or_create(asistente=asistente, defaults={'work_area': work_area, 'occupation': carrera_cargo})

                        # Enviar Email si se solicitó
                        email_status = "not_requested"
                        if send_emails:
                            try:
                                from .email import send_individual_confirmation_email
                                send_individual_confirmation_email(asistente)
                                email_status = "sent"
                            except Exception as email_err:
                                email_status = f"failed: {str(email_err)}"

                        return JsonResponse({
                            'status': 'success',
                            'action': action_taken,
                            'email_status': email_status,
                            'asistente': {
                                'first_name': asistente.first_name,
                                'last_name': asistente.last_name,
                                'email': asistente.email,
                                'dni': asistente.dni
                            }
                        })
                except Exception as db_err:
                    return JsonResponse({'status': 'error', 'message': str(db_err)})

        # 2. Manejo de POST AJAX para Analizar el archivo (Form Data)
        if request.method == 'POST' and request.POST.get('action') == 'parse' and request.FILES.get('excel_file'):
            excel_file = request.FILES['excel_file']
            try:
                if excel_file.name.endswith('.csv'):
                    df = pd.read_csv(excel_file)
                else:
                    df = pd.read_excel(excel_file)
                
                df.columns = [str(c).lower().strip() for c in df.columns]
                
                # Columnas requeridas
                required = ['nombre', 'apellido', 'email', 'dni']
                missing = [c for c in required if c not in df.columns]
                
                if missing:
                    return JsonResponse({'status': 'error', 'message': f"Faltan columnas obligatorias: {', '.join(missing)}"})
                
                edicion_activa = Edicion.objects.filter(activa=True).first()
                if not edicion_activa:
                    return JsonResponse({'status': 'error', 'message': "No hay una edición activa configurada."})

                rows = []
                for index, row in df.iterrows():
                    # Ignorar filas totalmente vacías
                    if pd.isna(row.get('nombre')) and pd.isna(row.get('apellido')) and pd.isna(row.get('dni')) and pd.isna(row.get('email')):
                        continue

                    dni_val = str(row.get('dni', '')).strip().split('.')[0]
                    email_val = str(row.get('email', '')).strip().lower()
                    nombre_val = str(row.get('nombre', '')).strip()
                    apellido_val = str(row.get('apellido', '')).strip()
                    telefono_val = str(row.get('telefono', '')).strip()
                    perfil_val = str(row.get('perfil', 'VISITOR')).upper().strip()
                    institucion_val = str(row.get('institucion', row.get('institución', ''))).strip()
                    carrera_val = str(row.get('carrera', '')).strip()
                    comision_val = str(row.get('comision', row.get('comisión', row.get('curso', '')))).strip()

                    # Convertir NaN a vacíos
                    if pd.isna(row.get('dni')): dni_val = ''
                    if pd.isna(row.get('email')): email_val = ''
                    if pd.isna(row.get('nombre')): nombre_val = ''
                    if pd.isna(row.get('apellido')): apellido_val = ''
                    if pd.isna(row.get('telefono')): telefono_val = ''
                    if pd.isna(row.get('perfil')): perfil_val = 'VISITOR'
                    if pd.isna(row.get('institucion')) and pd.isna(row.get('institución')): institucion_val = ''
                    if pd.isna(row.get('carrera')): carrera_val = ''
                    if pd.isna(row.get('comision')) and pd.isna(row.get('comisión')) and pd.isna(row.get('curso')): comision_val = ''

                    rows.append({
                        'index': index + 2,
                        'dni': dni_val,
                        'email': email_val,
                        'nombre': nombre_val,
                        'apellido': apellido_val,
                        'telefono': telefono_val,
                        'perfil': perfil_val,
                        'institucion': institucion_val,
                        'carrera': carrera_val,
                        'comision': comision_val
                    })
                return JsonResponse({'status': 'success', 'rows': rows, 'total': len(rows)})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f"Error al leer el archivo: {str(e)}"})

        # 3. Procesamiento tradicional (POST síncrono - fallback por compatibilidad)
        if request.method == 'POST' and request.FILES.get('excel_file'):
            excel_file = request.FILES['excel_file']
            send_emails = request.POST.get('send_emails') == 'yes'
            
            try:
                if excel_file.name.endswith('.csv'):
                    df = pd.read_csv(excel_file)
                else:
                    df = pd.read_excel(excel_file)
                
                df.columns = [str(c).lower().strip() for c in df.columns]
                
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
                        
                        for index, row in df.iterrows():
                            # Ignorar vacías
                            if pd.isna(row.get('nombre')) and pd.isna(row.get('apellido')) and pd.isna(row.get('dni')) and pd.isna(row.get('email')):
                                continue
                            
                            stats['total'] += 1
                            try:
                                with transaction.atomic():
                                    dni = str(row.get('dni')).strip().split('.')[0]
                                    email = str(row.get('email')).strip().lower()
                                    nombre = str(row.get('nombre', '')).strip()
                                    apellido = str(row.get('apellido', '')).strip()
                                    
                                    if not dni or not email or not nombre or not apellido:
                                        missing_fields = []
                                        if not dni: missing_fields.append("DNI")
                                        if not email: missing_fields.append("Email")
                                        if not nombre: missing_fields.append("Nombre")
                                        if not apellido: missing_fields.append("Apellido")
                                        raise ValueError(f"Datos básicos faltantes: {', '.join(missing_fields)}")

                                    profile_type = str(row.get('perfil', 'VISITOR')).upper().strip()
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

                                    Inscripcion.objects.get_or_create(
                                        asistente=asistente,
                                        edicion=edicion_activa
                                    )

                                    institucion = str(row.get('institucion', row.get('institución', ''))).strip()
                                    carrera_cargo = str(row.get('carrera', '')).strip()
                                    comision_excel = str(row.get('comision', row.get('comisión', row.get('curso', '')))).strip()

                                    if comision_excel:
                                        asistente.comision = comision_excel
                                        asistente.save()
                                    
                                    if institucion or carrera_cargo:
                                        from .models import DetalleEstudiante, DetalleDocente, DetalleProfesional
                                        if profile_type in [Asistente.ProfileType.STUDENT, Asistente.ProfileType.GRADUADO]:
                                            DetalleEstudiante.objects.update_or_create(asistente=asistente, defaults={'institution': institucion, 'career': carrera_cargo})
                                        elif profile_type == Asistente.ProfileType.TEACHER:
                                            DetalleDocente.objects.update_or_create(asistente=asistente, defaults={'institution': institucion, 'career_taught': carrera_cargo})
                                        elif profile_type in [Asistente.ProfileType.PROFESSIONAL, Asistente.ProfileType.OTRO]:
                                            work_area = institucion if profile_type == Asistente.ProfileType.PROFESSIONAL else "Otro"
                                            DetalleProfesional.objects.update_or_create(asistente=asistente, defaults={'work_area': work_area, 'occupation': carrera_cargo})

                                    if send_emails:
                                        try:
                                            from .email import send_individual_confirmation_email
                                            send_individual_confirmation_email(asistente)
                                        except Exception as e:
                                            stats['error_details'].append({'row': index + 2, 'msg': f"Registro OK, pero email falló: {str(e)}"})
                            
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
        Permite ver todos si se aplican filtros específicos y soporta multiselección sumada.
        """
        get_copy = request.GET.copy()
        comma_fields = {
            'profile_type': 'profile_type__in',
            'comision': 'comision__in',
            'inscripciones__edicion__id__exact': 'inscripciones__edicion__id__in',
        }
        
        custom_filters = {}
        for get_key, filter_lookup in comma_fields.items():
            val = get_copy.get(get_key)
            if val and ',' in val:
                custom_filters[filter_lookup] = val.split(',')
                del get_copy[get_key]

        original_GET = request.GET
        request.GET = get_copy
        try:
            qs = super().get_queryset(request)
        finally:
            request.GET = original_GET

        if custom_filters:
            qs = qs.filter(**custom_filters).distinct()

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
    actions = [
        'confirmar_asistencia', 
        'enviar_certificados', 
        'enviar_solicitud_actualizacion_dni', 
        'enviar_certificados_lote_40', 
        'exportar_no_estudiantes_xls', 
        'exportar_asistentes_xls',
        'set_perfil_estudiante',
        'set_perfil_docente',
        'set_perfil_profesional'
    ]
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

    # --- Método Visual Premium para Perfiles ---
    def perfil_badge(self, obj):
        colors = {
            'STUDENT':             ('#065f46', '#d1fae5', '🎓 Estudiante'),
            'GRADUADO':            ('#047857', '#ecfdf5', '🎓 Graduado'),
            'TEACHER':             ('#1e3a8a', '#dbeafe', '🏫 Docente'),
            'PROFESSIONAL':        ('#92400e', '#fef3c7', '💼 Profesional'),
            'PRESS':               ('#5b21b6', '#ede9fe', '📢 Prensa'),
            'GROUP_REPRESENTATIVE':('#3730a3', '#e0e7ff', '👥 Rep. Grupo'),
            'VISITOR':             ('#374151', '#f3f4f6', '👤 Visitante'),
            'OTRO':                ('#1f2937', '#e5e7eb', '❓ Otro'),
        }
        bg, fg, label = colors.get(obj.profile_type, ('#374151', '#f3f4f6', obj.get_profile_type_display()))
        return format_html(
            '<span style="background:{}; color:{}; padding:3px 10px; border-radius:12px; '
            'font-weight:600; font-size:11px; white-space:nowrap; display:inline-block;">{}</span>',
            fg, bg, label
        )
    perfil_badge.short_description = 'Perfil'
    perfil_badge.admin_order_field = 'profile_type'

    # --- Acciones Masivas Premium ---
    def set_perfil_estudiante(self, request, queryset):
        updated = queryset.update(profile_type='STUDENT')
        self.message_user(request, f'✅ {updated} asistentes actualizados a perfil Estudiante.')
    set_perfil_estudiante.short_description = '⚙️ Cambiar perfil de seleccionados a Estudiante'

    def set_perfil_docente(self, request, queryset):
        updated = queryset.update(profile_type='TEACHER')
        self.message_user(request, f'✅ {updated} asistentes actualizados a perfil Docente.')
    set_perfil_docente.short_description = '⚙️ Cambiar perfil de seleccionados a Docente'

    def set_perfil_profesional(self, request, queryset):
        updated = queryset.update(profile_type='PROFESSIONAL')
        self.message_user(request, f'✅ {updated} asistentes actualizados a perfil Profesional.')
    set_perfil_profesional.short_description = '⚙️ Cambiar perfil de seleccionados a Profesional'

class CertificadoAdmin(admin.ModelAdmin):
    class Media:
        js = ('admin/js/multiselect_filters.js',)

    list_display = ('asistente', 'tipo_certificado', 'email_enviado', 'fecha_envio', 'intentos', 'fecha_generacion')
    list_filter = ('tipo_certificado', 'email_enviado', 'fecha_generacion')
    search_fields = ('asistente__first_name', 'asistente__last_name', 'asistente__email')
    readonly_fields = ('fecha_generacion', 'fecha_envio', 'intentos')
    actions = ['enviar_por_email_accion_masiva']

    def get_queryset(self, request):
        get_copy = request.GET.copy()
        comma_fields = {
            'tipo_certificado': 'tipo_certificado__in',
            'email_enviado': 'email_enviado__in',
        }
        custom_filters = {}
        for get_key, filter_lookup in comma_fields.items():
            val = get_copy.get(get_key)
            if val and ',' in val:
                custom_filters[filter_lookup] = val.split(',')
                del get_copy[get_key]
                
        original_GET = request.GET
        request.GET = get_copy
        try:
            qs = super().get_queryset(request)
        finally:
            request.GET = original_GET
            
        if custom_filters:
            qs = qs.filter(**custom_filters).distinct()
        return qs

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
    change_list_template = "admin/api/programa/change_list.html"

    class Media:
        js = ('admin/js/multiselect_filters.js',)

    list_display = ('titulo', 'estado', 'categoria', 'aula', 'hora_inicio', 'hora_fin', 'dia', 'edicion')
    list_filter = ('estado', 'edicion', 'dia', 'categoria', 'aula')
    search_fields = ('titulo', 'descripcion', 'aula', 'categoria')
    list_editable = ('estado', 'aula', 'categoria', 'hora_inicio', 'hora_fin')
    filter_horizontal = ('disertantes',)
    save_on_top = True

    fieldsets = (
        ('Información General de la Charla', {
            'fields': ('titulo', 'edicion', 'estado', 'categoria', 'aula')
        }),
        ('Horarios y Fecha', {
            'fields': (('hora_inicio', 'hora_fin'), 'dia')
        }),
        ('Contenido y Disertantes', {
            'fields': ('descripcion', 'disertantes')
        }),
    )

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('importar-excel/', self.admin_site.admin_view(self.importar_excel_view), name='api_programa_importar_excel'),
            path('exportar-excel/', self.admin_site.admin_view(self.exportar_excel_view), name='api_programa_exportar_excel'),
            path('plantilla-excel/', self.admin_site.admin_view(self.descargar_plantilla_view), name='api_programa_plantilla_excel'),
        ]
        return custom_urls + urls

    def descargar_plantilla_view(self, request):
        from .services_programa import generar_plantilla_excel_programa
        return generar_plantilla_excel_programa()

    def exportar_excel_view(self, request):
        from .services_programa import exportar_excel_programa
        return exportar_excel_programa()

    def importar_excel_view(self, request):
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from io import BytesIO
        import base64
        from .models import Edicion
        from .services_programa import analizar_y_procesar_excel_programa

        context = self.admin_site.each_context(request)
        ediciones = Edicion.objects.all().order_by('-anio')

        if request.method == 'POST':
            action = request.POST.get('action')

            if action == 'preview':
                file_obj = request.FILES.get('file')
                if not file_obj:
                    self.message_user(request, "Debe seleccionar un archivo Excel (.xlsx).", messages.ERROR)
                    return redirect('admin:api_programa_importar_excel')

                # Procesar o Crear Edición seleccionada
                edicion_id = request.POST.get('edicion_id')
                edicion_obj = None

                if edicion_id == 'NUEVA':
                    nuevo_anio_raw = request.POST.get('nuevo_anio')
                    nuevo_nombre = request.POST.get('nuevo_nombre', '').strip()
                    hacer_activa = request.POST.get('hacer_activa') == 'true'

                    if not nuevo_anio_raw or not nuevo_anio_raw.isdigit():
                        self.message_user(request, "Debe ingresar un año válido para la nueva edición.", messages.ERROR)
                        return redirect('admin:api_programa_importar_excel')

                    anio_int = int(nuevo_anio_raw)
                    nombre_ed = nuevo_nombre or f"Congreso de Logística UNAB {anio_int}"
                    edicion_obj, created = Edicion.objects.get_or_create(
                        anio=anio_int,
                        defaults={'nombre': nombre_ed, 'activa': hacer_activa}
                    )
                    if hacer_activa:
                        edicion_obj.activa = True
                        edicion_obj.save()
                    if created:
                        self.message_user(request, f"Edición '{nombre_ed}' ({anio_int}) creada exitosamente.", messages.INFO)
                elif edicion_id and edicion_id.isdigit():
                    edicion_obj = Edicion.objects.filter(id=int(edicion_id)).first()

                if not edicion_obj:
                    edicion_obj = Edicion.objects.filter(activa=True).first()

                if not edicion_obj:
                    edicion_obj = Edicion.objects.create(anio=2026, nombre="Congreso de Logística UNAB 2026", activa=True)

                request.session['excel_edicion_id'] = edicion_obj.id

                # Guardar contenido del archivo en la sesión para la confirmación
                file_bytes = file_obj.read()
                file_obj.seek(0)
                request.session['excel_file_b64'] = base64.b64encode(file_bytes).decode('utf-8')

                resultado = analizar_y_procesar_excel_programa(file_obj, edicion=edicion_obj, commit=False)
                if not resultado.get('success'):
                    self.message_user(request, resultado.get('error', 'Error al analizar archivo.'), messages.ERROR)
                    return redirect('admin:api_programa_importar_excel')

                context.update({
                    'resumen': resultado['resumen'],
                    'filas': resultado['filas'],
                    'edicion_seleccionada': edicion_obj,
                    'ediciones': ediciones,
                    'title': f'Pre-flight Analysis - {edicion_obj.nombre}'
                })
                return render(request, 'admin/api/programa/importar_excel.html', context)

            elif action == 'commit':
                b64_file = request.session.get('excel_file_b64')
                ed_id = request.session.get('excel_edicion_id')
                if not b64_file:
                    self.message_user(request, "La sesión expiró. Por favor vuelva a cargar el archivo.", messages.ERROR)
                    return redirect('admin:api_programa_importar_excel')

                edicion_obj = Edicion.objects.filter(id=ed_id).first() if ed_id else Edicion.objects.filter(activa=True).first()

                file_bytes = base64.b64decode(b64_file)
                file_obj = BytesIO(file_bytes)

                filas_aprobadas_raw = request.POST.getlist('filas_aprobadas')
                filas_aprobadas = [int(f) for f in filas_aprobadas_raw if f.isdigit()]

                resultado = analizar_y_procesar_excel_programa(file_obj, edicion=edicion_obj, commit=True, filas_aprobadas=filas_aprobadas)
                if resultado.get('success'):
                    self.message_user(request, f"{resultado.get('mensaje', 'Importación completada.')} (Edición: {edicion_obj.nombre})", messages.SUCCESS)
                    request.session.pop('excel_file_b64', None)
                    request.session.pop('excel_edicion_id', None)
                    return redirect('admin:api_programa_changelist')
                else:
                    self.message_user(request, resultado.get('error', 'Error en la importación.'), messages.ERROR)
                    return redirect('admin:api_programa_importar_excel')

        context.update({
            'title': 'Ingesta e Importación del Programa (.xlsx)',
            'ediciones': ediciones
        })
        return render(request, 'admin/api/programa/importar_excel.html', context)

    def get_queryset(self, request):
        get_copy = request.GET.copy()
        comma_fields = {
            'edicion__id__exact': 'edicion__id__in',
            'categoria': 'categoria__in',
            'aula': 'aula__in',
        }
        custom_filters = {}
        for get_key, filter_lookup in comma_fields.items():
            val = get_copy.get(get_key)
            if val and ',' in val:
                custom_filters[filter_lookup] = val.split(',')
                del get_copy[get_key]
                
        original_GET = request.GET
        request.GET = get_copy
        try:
            qs = super().get_queryset(request)
        finally:
            request.GET = original_GET
            
        if custom_filters:
            qs = qs.filter(**custom_filters).distinct()
        return qs
    
    actions = ['aprobar_y_publicar', 'marcar_borrador', 'exportar_excel', 'descargar_plantilla_modelo', 'set_logistica', 'set_tecnologia']

    def aprobar_y_publicar(self, request, queryset):
        updated = queryset.update(estado='PUBLICADO')
        self.message_user(request, f"{updated} actividad(es) aprobada(s) y publicada(s) en la web.")
    aprobar_y_publicar.short_description = "Aprobar y publicar actividades en la web" # type: ignore

    def marcar_borrador(self, request, queryset):
        updated = queryset.update(estado='BORRADOR')
        self.message_user(request, f"{updated} actividad(es) cambiadas a borrador.")
    marcar_borrador.short_description = "Cambiar estado a Borrador" # type: ignore

    def exportar_excel(self, request, queryset):
        from .services_programa import exportar_programa_excel
        return exportar_programa_excel(queryset)
    exportar_excel.short_description = "Exportar agenda seleccionada a Excel / CSV" # type: ignore

    def descargar_plantilla_modelo(self, request, queryset):
        from .services_programa import generar_plantilla_excel_programa
        return generar_plantilla_excel_programa()
    descargar_plantilla_modelo.short_description = "Descargar Plantilla Oficial Excel (.xlsx)" # type: ignore

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
            'fields': ('nombre', 'empresa_institucion', 'foto', 'foto_url', 'tema_presentacion', 'linkedin')
        }),
        ('Información opcional', {
            'classes': ('collapse',),
            'fields': ('bio',),
        }),
    )
    list_display = ('nombre', 'empresa_institucion', 'tema_presentacion', 'edicion', 'linkedin')
    list_filter = ('edicion', 'estado')
    search_fields = ('nombre', 'empresa_institucion', 'tema_presentacion')
@admin.register(Empresa)
class EmpresaAdmin(SimpleHistoryAdmin):
    class Media:
        js = ('admin/js/multiselect_filters.js',)

    list_display = ('nombre_empresa', 'estado_badge', 'es_sponsor', 'edicion', 'numero_stand', 'cantidad_representantes', 'fecha_registro_detalle')
    list_filter = ('estado', 'es_sponsor', 'edicion', 'participo_edicion_anterior')
    search_fields = ('nombre_empresa', 'cuit', 'email_contacto', 'nombre_contacto')
    list_editable = ('numero_stand', 'cantidad_representantes')
    actions = ['confirmar_empresas', 'marcar_envio_bc', 'marcar_pendiente_pago', 'rechazar_empresas']
    readonly_fields = ('fecha_registro', 'fecha_revision', 'revisada_por')
    ordering = ['-fecha_registro']

    def fecha_registro_detalle(self, obj):
        return obj.fecha_registro.strftime("%d/%m/%Y %H:%M") if obj.fecha_registro else "-"
    fecha_registro_detalle.short_description = 'Fecha Inscripción'
    fecha_registro_detalle.admin_order_field = 'fecha_registro'

    def estado_badge(self, obj):
        colors = {
            'PENDIENTE':      ('#78716c', '#fafaf9'),  # Gris
            'ENVIO_BC':       ('#1d4ed8', '#eff6ff'),  # Azul
            'PENDIENTE_PAGO': ('#b45309', '#fffbeb'),  # Amarillo-naranja
            'CONFIRMADA':     ('#15803d', '#f0fdf4'),  # Verde
            'RECHAZADA':      ('#b91c1c', '#fef2f2'),  # Rojo
        }
        bg, fg = colors.get(obj.estado, ('#78716c', '#fafaf9'))
        label = obj.get_estado_display()
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;border-radius:12px;'
            'font-weight:600;font-size:12px;white-space:nowrap;">{}</span>',
            bg, fg, label
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado'
    fieldsets = (
        ('Identificación', {
            'fields': ('edicion', 'estado', 'es_sponsor', 'nombre_empresa', 'logo', 'cuit', 'descripcion', 'youtube_video_url')
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

    def confirmar_empresas(self, request, queryset):
        updated = queryset.update(estado='CONFIRMADA', fecha_revision=timezone.now(), revisada_por=request.user)
        self.message_user(request, f'✅ {updated} empresa(s) marcadas como CONFIRMADAS.')
    confirmar_empresas.short_description = '✅ Confirmar empresas seleccionadas'  # type: ignore

    def marcar_envio_bc(self, request, queryset):
        updated = queryset.update(estado='ENVIO_BC', fecha_revision=timezone.now(), revisada_por=request.user)
        self.message_user(request, f'📧 {updated} empresa(s) marcadas como Envío de B&C.')
    marcar_envio_bc.short_description = '📧 Marcar como Envío de Bases y Condiciones'  # type: ignore

    def marcar_pendiente_pago(self, request, queryset):
        updated = queryset.update(estado='PENDIENTE_PAGO', fecha_revision=timezone.now(), revisada_por=request.user)
        self.message_user(request, f'💳 {updated} empresa(s) marcadas como Pendiente de Pago.')
    marcar_pendiente_pago.short_description = '💳 Marcar como Pendiente de Pago'  # type: ignore

    def rechazar_empresas(self, request, queryset):
        updated = queryset.update(estado='RECHAZADA', fecha_revision=timezone.now(), revisada_por=request.user)
        self.message_user(request, f'❌ {updated} empresa(s) rechazada(s).')
    rechazar_empresas.short_description = '❌ Rechazar empresas seleccionadas'  # type: ignore

    def get_queryset(self, request):
        get_copy = request.GET.copy()
        comma_fields = {
            'estado': 'estado__in',
            'edicion__id__exact': 'edicion__id__in',
        }
        custom_filters = {}
        for get_key, filter_lookup in comma_fields.items():
            val = get_copy.get(get_key)
            if val and ',' in val:
                custom_filters[filter_lookup] = val.split(',')
                del get_copy[get_key]
                
        original_GET = request.GET
        request.GET = get_copy
        try:
            qs = super().get_queryset(request)
        finally:
            request.GET = original_GET
            
        if custom_filters:
            qs = qs.filter(**custom_filters).distinct()
        return qs


class EjeTematicoFilter(admin.SimpleListFilter):
    title = 'Eje Temático'
    parameter_name = 'eje_tematico'

    def lookups(self, request, model_admin):
        return [
            ("TECNOLOGIA", "Tecnología"),
            ("LOGISTICA", "Logística"),
            ("PUERTOS/COMERCIO EXTERIOR", "Puertos/Comercio Exterior"),
            ("E-COMMERS", "E-Commerce"),
            ("SUPPLY CHAIN", "Supply Chain"),
            ("CAPITAL HUMANO", "Capital Humano"),
            ("RADIO", "Radio"),
            ("SUSTENTABILIDAD", "Sustentabilidad"),
            ("TRANSPORTE", "Transporte"),
        ]

    def queryset(self, request, queryset):
        if self.value():
            valores = self.value().split(',')
            q_obj = models.Q()
            for val in valores:
                q_obj |= models.Q(ejes_tematicos__icontains=val)
            return queryset.filter(q_obj).distinct()
        return queryset


@admin.register(PostulacionDisertante)
class PostulacionDisertanteAdmin(SimpleHistoryAdmin):
    class Media:
        js = ('admin/js/multiselect_filters.js',)

    list_display = ('nombre_apellido', 'email', 'titulo_charla', 'estado', 'edicion', 'fecha_postulacion_detalle')
    list_filter = ('estado', 'edicion', EjeTematicoFilter, 'modalidad')
    search_fields = ('nombre_apellido', 'dni', 'email', 'titulo_charla')
    list_editable = ('estado',)
    actions = ['aprobar_postulaciones', 'generar_borrador_programa', 'rechazar_postulaciones']
    readonly_fields = ('fecha_postulacion', 'fecha_revision', 'revisada_por')
    ordering = ['-fecha_postulacion']

    def generar_borrador_programa(self, request, queryset):
        from .services_programa import generar_borrador_programa_desde_postulaciones
        progs, disertantes = generar_borrador_programa_desde_postulaciones(queryset)
        self.message_user(request, f'Se crearon/actualizaron {progs} borrador(es) de actividades en Programa con {disertantes} disertante(s) asignado(s).')
    generar_borrador_programa.short_description = 'Generar borrador en el Programa (unificando ponencias)'  # type: ignore

    def fecha_postulacion_detalle(self, obj):
        return obj.fecha_postulacion.strftime("%d/%m/%Y %H:%M") if obj.fecha_postulacion else "-"
    fecha_postulacion_detalle.short_description = 'Fecha Postulación'
    fecha_postulacion_detalle.admin_order_field = 'fecha_postulacion'
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
        from .services import sync_postulacion_a_disertante
        sync_postulacion_a_disertante(obj)

    def aprobar_postulaciones(self, request, queryset):
        from .services import sync_postulacion_a_disertante
        count = 0
        for obj in queryset:
            obj.estado = 'APROBADO'
            obj.fecha_revision = timezone.now()
            obj.revisada_por = request.user
            obj.save()
            sync_postulacion_a_disertante(obj)
            count += 1
        self.message_user(request, f'{count} postulacion(es) de disertante aprobada(s).')
    aprobar_postulaciones.short_description = 'Aprobar postulaciones seleccionadas'  # type: ignore

    def rechazar_postulaciones(self, request, queryset):
        from .services import sync_postulacion_a_disertante
        count = 0
        for obj in queryset:
            obj.estado = 'RECHAZADO'
            obj.fecha_revision = timezone.now()
            obj.revisada_por = request.user
            obj.save()
            sync_postulacion_a_disertante(obj)
            count += 1
        self.message_user(request, f'{count} postulacion(es) de disertante rechazada(s).')
    rechazar_postulaciones.short_description = 'Rechazar postulaciones seleccionadas'  # type: ignore

    def get_queryset(self, request):
        get_copy = request.GET.copy()
        comma_fields = {
            'estado': 'estado__in',
            'edicion__id__exact': 'edicion__id__in',
            'modalidad': 'modalidad__in',
        }
        custom_filters = {}
        for get_key, filter_lookup in comma_fields.items():
            val = get_copy.get(get_key)
            if val and ',' in val:
                custom_filters[filter_lookup] = val.split(',')
                del get_copy[get_key]
                
        original_GET = request.GET
        request.GET = get_copy
        try:
            qs = super().get_queryset(request)
        finally:
            request.GET = original_GET
            
        if custom_filters:
            qs = qs.filter(**custom_filters).distinct()
        return qs


@admin.register(InscripcionPrensa)
class InscripcionPrensaAdmin(admin.ModelAdmin):
    class Media:
        js = ('admin/js/multiselect_filters.js',)

    list_display = ('nombre_apellido', 'tipo_perfil', 'medio_o_canal', 'edicion', 'fecha_inscripcion_detalle', 'link_display')
    list_filter = ('tipo_perfil', 'edicion')
    search_fields = ('nombre_apellido', 'dni', 'email', 'medio_o_canal')

    def get_queryset(self, request):
        get_copy = request.GET.copy()
        comma_fields = {
            'tipo_perfil': 'tipo_perfil__in',
            'edicion__id__exact': 'edicion__id__in',
        }
        custom_filters = {}
        for get_key, filter_lookup in comma_fields.items():
            val = get_copy.get(get_key)
            if val and ',' in val:
                custom_filters[filter_lookup] = val.split(',')
                del get_copy[get_key]
                
        original_GET = request.GET
        request.GET = get_copy
        try:
            qs = super().get_queryset(request)
        finally:
            request.GET = original_GET
            
        if custom_filters:
            qs = qs.filter(**custom_filters).distinct()
        return qs
    readonly_fields = ('fecha_inscripcion',)
    ordering = ['-fecha_inscripcion']

    def fecha_inscripcion_detalle(self, obj):
        return obj.fecha_inscripcion.strftime("%d/%m/%Y %H:%M") if obj.fecha_inscripcion else "-"
    fecha_inscripcion_detalle.short_description = 'Fecha Inscripción'
    fecha_inscripcion_detalle.admin_order_field = 'fecha_inscripcion'
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