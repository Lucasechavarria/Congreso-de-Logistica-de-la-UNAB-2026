import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from api.models import Inscripcion, Edicion
from .models import OfertaLaboral

logger = logging.getLogger(__name__)

@shared_task
def enviar_newsletter_semanal():
    """
    Tarea programada para enviar el resumen semanal de ofertas laborales
    a todos los asistentes que aceptaron recibir alertas.
    """
    # 1. Obtener edición activa
    edicion_activa = Edicion.objects.filter(activa=True).first()
    if not edicion_activa:
        logger.warning("No hay edición activa configurada para el newsletter.")
        return "No hay edición activa"

    # 2. Obtener ofertas aprobadas de los últimos 7 días
    hace_siete_dias = timezone.now() - timedelta(days=7)
    ofertas = OfertaLaboral.objects.filter(
        estado='APROBADO',
        fecha_creacion__gte=hace_siete_dias
    ).order_by('-fecha_creacion')

    if not ofertas.exists():
        logger.info("No hay nuevas ofertas para enviar en el newsletter semanal.")
        return "Sin ofertas nuevas"

    # 3. Obtener asistentes que desean alertas en esta edición
    suscritos = Inscripcion.objects.filter(
        edicion=edicion_activa,
        desea_alertas_laborales=True
    ).select_related('asistente')

    if not suscritos.exists():
        logger.info("No hay suscriptores para el newsletter.")
        return "Sin suscriptores"

    # 4. Preparar el contenido del email (general para todos para eficiencia)
    sujeto = f"💼 Nuevas Vacantes de la Semana - {edicion_activa.nombre}"
    
    # Renderizar HTML
    html_content = render_to_string('email/newsletter_ofertas.html', {
        'ofertas': ofertas,
        'edicion': edicion_activa,
        'STATIC_URL': settings.STATIC_URL if hasattr(settings, 'STATIC_URL') else '/static/',
    })
    text_content = strip_tags(html_content)

    # 5. Envío masivo (BCC o individual para personalización de desuscripción)
    # Por ahora individual para que el link de desuscripción pueda ser personalizado por ID (opcional)
    enviados = 0
    for inscripcion in suscritos:
        try:
            email = EmailMultiAlternatives(
                sujeto,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [inscripcion.asistente.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            enviados += 1
        except Exception as e:
            logger.error(f"Error enviando newsletter a {inscripcion.asistente.email}: {e}")

    return f"Newsletter enviado a {enviados} suscriptores."

@shared_task
def enviar_email_postulacion(postulacion_id):
    """
    Envía notificaciones por email tanto a la empresa como al postulante.
    """
    from .models import PostulacionOferta
    try:
        postulacion = PostulacionOferta.objects.get(id=postulacion_id)
        oferta = postulacion.oferta
        empresa = oferta.empresa

        # 1. Email para la empresa (Notificación de nuevo candidato)
        subject_empresa = f"🚀 Nuevo Candidato: {postulacion.nombre_completo} - {oferta.titulo_puesto}"
        html_empresa = render_to_string('email/postulacion_empresa.html', {
            'postulacion': postulacion,
            'oferta': oferta,
            'empresa': empresa,
        })
        text_empresa = strip_tags(html_empresa)
        
        email_to_empresa = EmailMultiAlternatives(
            subject_empresa,
            text_empresa,
            settings.DEFAULT_FROM_EMAIL,
            [empresa.email_contacto]
        )
        email_to_empresa.attach_alternative(html_empresa, "text/html")
        
        # Adjuntar CV si existe
        if postulacion.cv:
            try:
                # Abrir el archivo y leerlo
                cv_file = postulacion.cv.open('rb')
                email_to_empresa.attach(
                    f"CV_{postulacion.nombre_completo.replace(' ', '_')}.pdf",
                    cv_file.read(),
                    'application/pdf'
                )
                cv_file.close()
            except Exception as e:
                logger.error(f"Error adjuntando CV al email: {e}")

        email_to_empresa.send()

        # 2. Email para el postulante (Confirmación de recepción)
        subject_postulante = f"✅ Tu postulación ha sido enviada: {oferta.titulo_puesto}"
        html_postulante = render_to_string('email/postulacion_confirmacion.html', {
            'postulacion': postulacion,
            'oferta': oferta,
            'empresa': empresa,
        })
        text_postulante = strip_tags(html_postulante)
        
        email_to_postulante = EmailMultiAlternatives(
            subject_postulante,
            text_postulante,
            settings.DEFAULT_FROM_EMAIL,
            [postulacion.email]
        )
        email_to_postulante.attach_alternative(html_postulante, "text/html")
        email_to_postulante.send()

        return f"Notificaciones enviadas exitosamente para postulación {postulacion_id}"
    except PostulacionOferta.DoesNotExist:
        logger.error(f"Postulación {postulacion_id} no encontrada en la tarea asíncrona.")
        return "Postulación no encontrada"
    except Exception as e:
        logger.error(f"Error general en enviar_email_postulacion: {e}")
        return str(e)
