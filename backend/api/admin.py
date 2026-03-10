from django.contrib import admin
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
import json
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Disertante, Empresa, Asistente, Inscripcion, Certificado, Programa
from .email import send_certificate_email


def get_stats_data():
    """
    Helper para obtener los datos de estadísticas.
    """
    # 1. Inscripciones por día (últimos 30 días)
    hace_30_dias = timezone.now() - timezone.timedelta(days=30)
    inscripciones_por_dia = Inscripcion.objects.filter(
        fecha_inscripcion__gte=hace_30_dias
    ).annotate(
        date=TruncDate('fecha_inscripcion')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    daily_stats = [
        {'date': item['date'].strftime('%Y-%m-%d'), 'count': item['count']}
        for item in inscripciones_por_dia
    ]

    # 2. Comparativa por Edición
    ediciones_stats = Inscripcion.objects.values(
        'edicion__nombre'
    ).annotate(
        total=Count('id')
    ).order_by('edicion__nombre')

    comparative_stats = [
        {'name': item['edicion__nombre'], 'total': item['total']}
        for item in ediciones_stats
    ]

    # 3. Distribución por Tipo de Perfil (Solo edición activa)
    perfil_stats = Asistente.objects.filter(
        inscripciones__edicion__activa=True
    ).values(
        'profile_type'
    ).annotate(
        value=Count('id')
    )

    # Mapeo de tipos de perfil a nombres legibles
    profile_map = dict(Asistente.ProfileType.choices)
    distribution_stats = [
        {'name': profile_map.get(item['profile_type'], item['profile_type']), 'value': item['value']}
        for item in perfil_stats
    ]

    # 4. KPIs Generales
    total_inscritos = Inscripcion.objects.filter(edicion__activa=True).count()
    total_confirmados = Asistente.objects.filter(
        inscripciones__edicion__activa=True,
        asistencia_confirmada=True
    ).count()

    return {
        'daily_stats': daily_stats,
        'comparative_stats': comparative_stats,
        'distribution_stats': distribution_stats,
        'kpis': {
            'total_inscritos': total_inscritos,
            'total_confirmados': total_confirmados,
            'asistencia_ratio': round((total_confirmados / total_inscritos * 100), 2) if total_inscritos > 0 else 0
        }
    }


def admin_dashboard(request):
    """
    Vista personalizada para el dashboard en el panel admin.
    """
    stats = get_stats_data()
    context = {
        **admin.site.each_context(request),
        'title': 'Dashboard de Analíticas',
        **stats
    }
    return render(request, 'admin/dashboard.html', context)


# Inyectar el dashboard en el Admin de Django
original_get_urls = admin.site.get_urls

def get_urls():
    urls = original_get_urls()
    custom_urls = [
        path('dashboard/', admin.site.admin_view(admin_dashboard), name='admin-dashboard'),
    ]
    return custom_urls + urls

admin.site.get_urls = get_urls
# Cambiar el título del índice para incluir un link directo (opcional pero útil)
admin.site.index_title = "Administración del Congreso - [Ir al Dashboard](/admin/dashboard/)"




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


class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('asistente', 'empresa', 'fecha_inscripcion')
    list_filter = ('fecha_inscripcion',)
    search_fields = ('asistente__first_name', 'asistente__last_name', 'asistente__email', 'empresa__razon_social')

class AsistenteAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'dni', 'asistencia_confirmada', 'fecha_confirmacion')
    list_filter = (DNIFilter, 'asistencia_confirmada', 'fecha_confirmacion')
    search_fields = ('first_name', 'last_name', 'email', 'dni')
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

        for row, asistente in enumerate(asistentes, start=1):
            for col, campo in enumerate(campos):
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

        # Escribir datos
        for row, asistente in enumerate(asistentes, start=1):
            for col, campo in enumerate(campos):
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
        updated_count = 0
        for asistente in queryset:
            if not asistente.asistencia_confirmada:
                asistente.asistencia_confirmada = True
                asistente.fecha_confirmacion = timezone.now()
                asistente.save()
                
                # Crear certificado de asistencia
                certificado, created = Certificado.objects.get_or_create(
                    asistente=asistente,
                    tipo_certificado=Certificado.TipoCertificado.ASISTENCIA
                )
                
                # Enviar certificado por email
                send_certificate_email(certificado)
                updated_count += 1
        
        self.message_user(request, f"{updated_count} asistencias confirmadas y certificados enviados.")
    confirmar_asistencia.short_description = "Confirmar asistencia y enviar certificado"  # type: ignore

    def enviar_certificados(self, request, queryset):
        sent_count = 0
        for asistente in queryset.filter(asistencia_confirmada=True):
            certificado, created = Certificado.objects.get_or_create(
                asistente=asistente,
                tipo_certificado=Certificado.TipoCertificado.ASISTENCIA
            )
            send_certificate_email(certificado)
            sent_count += 1
        
        self.message_user(request, f"{sent_count} certificados enviados.")
    enviar_certificados.short_description = "Enviar certificados a asistentes confirmados"  # type: ignore

class CertificadoAdmin(admin.ModelAdmin):
    list_display = ('asistente', 'tipo_certificado', 'fecha_generacion')
    list_filter = ('tipo_certificado', 'fecha_generacion')
    search_fields = ('asistente__first_name', 'asistente__last_name', 'asistente__email')

class ProgramaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'aula', 'dia', 'hora_inicio', 'hora_fin')
    list_filter = ('dia', 'categoria', 'aula')
    search_fields = ('titulo',)
    list_editable = ('categoria',)

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
    list_display = ('nombre', 'tema_presentacion', 'linkedin')
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('nombre_empresa', 'logo')
        }),
        ('Información opcional', {
            'classes': ('collapse',),
            'fields': (
                'cuit', 'direccion', 'telefono_empresa', 'email_empresa', 'sitio_web', 'descripcion',
                'nombre_contacto', 'email_contacto', 'celular_contacto', 'cargo_contacto',
                'participacion_opciones', 'participacion_otra',
            ),
        }),
    )
    list_display = ('nombre_empresa', 'logo')
admin.site.register(Asistente, AsistenteAdmin)
admin.site.register(Inscripcion, InscripcionAdmin)
admin.site.register(Certificado, CertificadoAdmin)
admin.site.register(Programa, ProgramaAdmin)