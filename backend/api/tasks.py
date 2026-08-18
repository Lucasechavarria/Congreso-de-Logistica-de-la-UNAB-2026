import logging
from celery import shared_task
from .models import Asistente, Certificado
from .email import (
    send_individual_confirmation_email,
    send_group_confirmation_emails,
    send_certificate_email,
    send_admin_email_failure_alert
)

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def task_enviar_confirmacion_individual(self, asistente_id):
    """
    Envía el email de confirmación de inscripción individual de fondo.
    Soporta reintentos automáticos ante fallas temporales de red o del SMTP universitario.
    Si agota los reintentos, envía un auto-email de alerta a la administración.
    """
    try:
        asistente = Asistente.objects.get(id=asistente_id)
        success = send_individual_confirmation_email(asistente)
        if not success:
            raise Exception("Fallo en el transporte SMTP del servidor universitario.")
        logger.info(f"[SUCCESS] Email de confirmación individual enviado a {asistente.email}")
        return True
    except Exception as exc:
        logger.error(f"[ERROR] Falló el envío individual para asistente {asistente_id}: {exc}.")
        if self.request.retries >= self.max_retries:
            try:
                asistente = Asistente.objects.get(id=asistente_id)
                send_admin_email_failure_alert(asistente, exc)
            except Exception as alert_err:
                logger.error(f"[CRITICAL] No se pudo enviar la auto-alerta a administración: {alert_err}")
            return False
        self.retry(exc=exc)

@shared_task(bind=True, max_retries=3, default_retry_delay=90)
def task_enviar_confirmacion_grupal(self, representante_id):
    """
    Genera el archivo Excel de miembros y envía los correos masivos a todo el grupo
    en segundo plano de forma completamente asíncrona.
    """
    try:
        representante = Asistente.objects.get(id=representante_id)
        resultado = send_group_confirmation_emails(representante)
        logger.info(
            f"[SUCCESS] Envío de correos grupales completado para representante {representante.email}. "
            f"Enviados: {resultado.get('total_emails')}, Fallidos: {resultado.get('total_fallidos')}"
        )
        return resultado
    except Exception as exc:
        logger.error(f"[ERROR] Falló el envío de correos grupales para representante {representante_id}: {exc}.")
        if self.request.retries >= self.max_retries:
            try:
                representante = Asistente.objects.get(id=representante_id)
                send_admin_email_failure_alert(representante, exc)
            except Exception as alert_err:
                logger.error(f"[CRITICAL] No se pudo enviar la auto-alerta a administración: {alert_err}")
            return False
        self.retry(exc=exc)

@shared_task(bind=True, max_retries=5, default_retry_delay=120)
def task_generar_y_enviar_certificado(self, certificado_id):
    """
    Genera el PDF del certificado (proceso pesado de Pillow en CPU) y lo envía
    vía correo electrónico de forma asíncrona no-bloqueante.
    """
    try:
        certificado = Certificado.objects.get(id=certificado_id)
        success = send_certificate_email(certificado)
        if not success:
            raise Exception("Fallo en la generación o el envío SMTP del certificado.")
        logger.info(f"[SUCCESS] Certificado {certificado_id} procesado y enviado al asistente.")
        return True
    except Exception as exc:
        logger.error(f"[ERROR] Falló el procesamiento del certificado {certificado_id}: {exc}. Reintentando...")
        self.retry(exc=exc)
