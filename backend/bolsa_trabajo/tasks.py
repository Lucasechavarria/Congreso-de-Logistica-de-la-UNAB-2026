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
