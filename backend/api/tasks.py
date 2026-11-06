import logging
import time
from celery import shared_task
from django.utils import timezone
from .models import Asistente, Certificado, Inscripcion
from .email import (
    send_individual_confirmation_email,
    send_group_confirmation_emails,
    send_certificate_email,
    send_attendance_confirmation_email,
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
        is_eager = getattr(self.request, 'is_eager', False)
        if self.request.retries >= self.max_retries or is_eager:
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
        is_eager = getattr(self.request, 'is_eager', False)
        if self.request.retries >= self.max_retries or is_eager:
            try:
                representante = Asistente.objects.get(id=representante_id)
                send_admin_email_failure_alert(representante, exc)
            except Exception as alert_err:
                logger.error(f"[CRITICAL] No se pudo enviar la auto-alerta a administración: {alert_err}")
            return False
        self.retry(exc=exc)

@shared_task(bind=True, max_retries=1, default_retry_delay=120)
def task_generar_y_enviar_certificado(self, certificado_id):
    """
    Genera el PDF del certificado (proceso pesado de Pillow en CPU) y lo envía
    vía correo electrónico de forma asíncrona no-bloqueante.
    Evita reintentos múltiples cuando el correo del participante es inválido
    para no generar rebotes (bounces) en la casilla del evento.
    """
    try:
        certificado = Certificado.objects.get(id=certificado_id)
        result = send_certificate_email(certificado)
        success = result[0] if isinstance(result, tuple) else bool(result)
        error_detail = result[1] if isinstance(result, tuple) and len(result) > 1 else "Fallo en la generación o el envío SMTP del certificado."

        if not success:
            # Si el fallo es por correo inválido, typo de dominio, placeholder o rechazo permanente 550/553, no reintentar
            err_lower = str(error_detail).lower()
            errores_permanentes = (
                "formato del correo",
                "error de tipeo",
                "marcador interno",
                "no tiene un correo",
                "550",
                "553",
                "invalid",
                "user unknown",
                "address not found",
            )
            if any(token in err_lower for token in errores_permanentes):
                logger.warning(f"[NO-RETRY] Certificado {certificado_id} con error permanente de destinatario: {error_detail}")
                return False
            raise Exception(error_detail)

        logger.info(f"[SUCCESS] Certificado {certificado_id} procesado y enviado al asistente.")
        return True
    except Exception as exc:
        logger.error(f"[ERROR] Falló el procesamiento del certificado {certificado_id}: {exc}.")
        is_eager = getattr(self.request, 'is_eager', False)
        if self.request.retries >= self.max_retries or is_eager:
            return False
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def task_enviar_confirmacion_asistencia(self, asistente_id, inscripcion_id=None):
    """
    Envía de forma asíncrona el email institucional de confirmación de asistencia
    al momento en que el participante se acredita (check-in QR o DNI).
    """
    try:
        asistente = Asistente.objects.get(id=asistente_id)
        inscripcion = None
        if inscripcion_id:
            try:
                inscripcion = Inscripcion.objects.get(id=inscripcion_id)
            except Inscripcion.DoesNotExist:
                pass
        success = send_attendance_confirmation_email(asistente, inscripcion)
        if not success:
            raise Exception("No se pudo entregar el correo de confirmación de asistencia.")
        logger.info(f"[SUCCESS] Confirmación de asistencia enviada a {asistente.email}")
        return True
    except Exception as exc:
        logger.error(f"[ERROR] Falló el envío de confirmación de asistencia para asistente {asistente_id}: {exc}")
        is_eager = getattr(self.request, 'is_eager', False)
        if self.request.retries >= self.max_retries or is_eager:
            return False
        self.retry(exc=exc)


@shared_task(bind=True)
def task_procesar_cola_certificados_lote(self, batch_size=10, forzar=False, delay_seconds=2):
    """
    Procesa un lote controlado de certificados pendientes para emisión y envío.
    Regla de seguridad: Si forzar=False, bloquea el envío antes de las 18:00 hs (hora oficial Argentina GMT-3).
    Aplica una pausa configurable entre envíos para proteger CPU de Pillow y SMTP.
    """
    ahora_local = timezone.localtime(timezone.now())
    if not forzar and ahora_local.hour < 18:
        msg = f"Envío bloqueado preventivamente: La hora actual ({ahora_local.strftime('%H:%M:%S')}) es anterior a las 18:00 hs oficial."
        logger.warning(f"[CERTIFICADOS BATCH] {msg}")
        return {
            'status': 'blocked_by_time',
            'message': msg,
            'processed': 0,
            'errors': 0,
            'remaining': Certificado.objects.filter(email_enviado=False).count(),
            'logs': [msg]
        }

    certificados = list(Certificado.objects.filter(email_enviado=False).order_by('id')[:batch_size])
    logs = []
    processed = 0
    errors = 0

    logger.info(f"[CERTIFICADOS BATCH] Iniciando procesamiento de lote ({len(certificados)} certificados, delay={delay_seconds}s)...")

    for cert in certificados:
        destinatario = getattr(cert.asistente, 'email', '') or f"Asistente #{cert.asistente_id}"
        try:
            result = send_certificate_email(cert)
            success = result[0] if isinstance(result, tuple) else bool(result)
            if success:
                logs.append(f"✓ Certificado enviado con éxito a {destinatario}")
                processed += 1
            else:
                motivo = result[1] if isinstance(result, tuple) and len(result) > 1 else "Error en el transporte SMTP"
                logs.append(f"✗ Error al enviar a {destinatario}: {motivo}")
                errors += 1
        except Exception as e:
            logs.append(f"✗ Excepción con {destinatario}: {str(e)}")
            errors += 1

        if delay_seconds > 0:
            time.sleep(delay_seconds)

    remaining = Certificado.objects.filter(email_enviado=False).count()
    return {
        'status': 'ok',
        'processed': processed,
        'errors': errors,
        'remaining': remaining,
        'logs': logs
    }


@shared_task(bind=True)
def task_ejecutar_backup_dual_gdrive(self):
    """
    Tarea programada por Celery Beat para generar el respaldo dual y subirlo
    a los Google Drive Personal e Institucional en los horarios estipulados.
    """
    from .gdrive_backup_service import ejecutar_backup_completo
    try:
        resultado = ejecutar_backup_completo()
        logger.info(f"[BACKUP GDRIVE TASK] Ejecución finalizada: {resultado.get('status')} - {resultado.get('archivo')}")
        return resultado
    except Exception as exc:
        logger.error(f"[BACKUP GDRIVE TASK] Error crítico ejecutando backup: {exc}")
        return {'status': 'error', 'error': str(exc)}




