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
def task_procesar_cola_certificados_lote(self, batch_size=5, forzar=False, delay_seconds=1, reintentar_fallidos=False):
    """
    Procesa un lote controlado de certificados pendientes para emisión y envío.
    Coordina mediante pg_try_advisory_lock y select_for_update(skip_locked=True) en PostgreSQL
    para no colisionar con la consola web (/admin/certificate-queue/) ni con otros workers.
    """
    from django.core.mail import get_connection
    from .services import sincronizar_certificados_asistencia
    from .scheduler import (
        es_horario_habilitado_certificados,
        acquire_certificate_queue_lock,
        reclamar_lote_certificados,
        is_web_console_priority_active,
    )

    try:
        sincronizar_certificados_asistencia()
    except Exception as sync_err:
        logger.warning(f"[CERTIFICADOS BATCH] Error sincronizando asistencias: {sync_err}")

    ahora_local = timezone.localtime(timezone.now())
    if not forzar and not es_horario_habilitado_certificados(ahora_local):
        msg = f"Envío bloqueado preventivamente: La hora actual ({ahora_local.strftime('%H:%M:%S')}) es anterior a las 18:00 hs oficial."
        logger.warning(f"[CERTIFICADOS BATCH] {msg}")
        return {
            'status': 'blocked_by_time',
            'message': msg,
            'processed': 0,
            'errors': 0,
            'remaining': Certificado.objects.filter(email_enviado=False).count(),
            'remaining_unattempted': Certificado.objects.filter(email_enviado=False, intentos=0).count(),
            'failed_count': Certificado.objects.filter(email_enviado=False, intentos__gt=0).count(),
            'logs': [msg]
        }

    if not forzar and is_web_console_priority_active():
        return {
            'status': 'busy_web_or_worker',
            'processed': 0,
            'errors': 0,
            'remaining': Certificado.objects.filter(email_enviado=False).count(),
            'remaining_unattempted': Certificado.objects.filter(email_enviado=False, intentos=0).count(),
            'failed_count': Certificado.objects.filter(email_enviado=False, intentos__gt=0).count(),
            'logs': ['⏳ Consola web con prioridad activa; cediendo ejecución.']
        }

    with acquire_certificate_queue_lock() as acquired:
        if not acquired:
            return {
                'status': 'busy_web_or_worker',
                'processed': 0,
                'errors': 0,
                'remaining': Certificado.objects.filter(email_enviado=False).count(),
                'remaining_unattempted': Certificado.objects.filter(email_enviado=False, intentos=0).count(),
                'failed_count': Certificado.objects.filter(email_enviado=False, intentos__gt=0).count(),
                'logs': ['⏳ Consola web u otro worker activo en PostgreSQL; cediendo prioridad.']
            }

        certificados = reclamar_lote_certificados(
            batch_size=batch_size,
            reintentar_fallidos=reintentar_fallidos,
            after_id=0,
            max_intentos_auto=3 if reintentar_fallidos else None,
        )

        logs = []
        processed = 0
        errors = 0

        if not certificados:
            remaining = Certificado.objects.filter(email_enviado=False).count()
            return {
                'status': 'ok',
                'processed': 0,
                'errors': 0,
                'remaining': remaining,
                'remaining_unattempted': Certificado.objects.filter(email_enviado=False, intentos=0).count(),
                'failed_count': Certificado.objects.filter(email_enviado=False, intentos__gt=0).count(),
                'logs': []
            }

        logger.info(f"[CERTIFICADOS BATCH] Iniciando procesamiento de lote ({len(certificados)} certificados, delay={delay_seconds}s)...")
        batch_start = time.monotonic()
        MAX_BATCH_SECONDS = 12.0

        smtp_conn = None
        smtp_open_failed = False
        try:
            smtp_conn = get_connection(fail_silently=False)
            smtp_conn.open()
        except Exception as conn_err:
            logger.warning(f"[CERTIFICADOS BATCH] No se pudo pre-abrir conexión SMTP: {conn_err}")
            smtp_conn = None
            smtp_open_failed = True

        try:
            for idx, cert in enumerate(certificados):
                if (time.monotonic() - batch_start) >= MAX_BATCH_SECONDS:
                    break

                try:
                    cert.refresh_from_db(fields=['email_enviado', 'intentos'])
                    if cert.email_enviado:
                        processed += 1
                        continue
                except Exception:
                    pass

                destinatario = getattr(cert.asistente, 'email', '') or f"Asistente #{cert.asistente_id}"
                try:
                    result = send_certificate_email(cert, connection=smtp_conn)
                    success = result[0] if isinstance(result, tuple) else bool(result)
                    if success:
                        logs.append(f"✓ Certificado enviado con éxito a {destinatario}")
                        processed += 1
                    else:
                        motivo = result[1] if isinstance(result, tuple) and len(result) > 1 else "Error en el transporte SMTP"
                        logs.append(f"✗ Error al enviar a {destinatario}: {motivo}")
                        errors += 1
                        es_error_smtp = "Fallo en PDF o SMTP" in str(motivo)
                        if smtp_open_failed and es_error_smtp:
                            break
                        if (
                            smtp_conn is not None
                            and es_error_smtp
                            and idx < len(certificados) - 1
                            and (time.monotonic() - batch_start) < MAX_BATCH_SECONDS
                        ):
                            try:
                                smtp_conn.close()
                                smtp_conn.open()
                            except Exception:
                                smtp_conn = None
                                break
                except Exception as e:
                    logs.append(f"✗ Excepción con {destinatario}: {str(e)}")
                    errors += 1
                    if smtp_open_failed:
                        break

                if delay_seconds > 0 and idx < len(certificados) - 1:
                    if (time.monotonic() - batch_start + delay_seconds) < MAX_BATCH_SECONDS:
                        time.sleep(delay_seconds)
        finally:
            if smtp_conn is not None:
                try:
                    smtp_conn.close()
                except Exception:
                    pass

        remaining = Certificado.objects.filter(email_enviado=False).count()
        remaining_unattempted = Certificado.objects.filter(email_enviado=False, intentos=0).count()
        failed_count = Certificado.objects.filter(email_enviado=False, intentos__gt=0).count()
        return {
            'status': 'ok',
            'processed': processed,
            'errors': errors,
            'remaining': remaining,
            'remaining_unattempted': remaining_unattempted,
            'failed_count': failed_count,
            'logs': logs
        }


@shared_task(bind=True)
def task_ejecutar_respaldo_programado(self, manual=False):
    """
    Los respaldos programados automáticos fueron eliminados por decisión de administración.
    Solo ejecuta si se invoca explícitamente con manual=True.
    """
    if not manual:
        logger.info("[BACKUP TASK] Ejecución automática omitida: los respaldos del sistema son exclusivamente manuales.")
        return {'status': 'skipped', 'ok': False, 'reason': 'manual_only'}
    from .backup_service import ejecutar_respaldo_programado
    try:
        resultado = ejecutar_respaldo_programado()
        logger.info(f"[BACKUP TASK] Respaldo manual finalizado: {resultado.get('status')} - {resultado.get('archivo')}")
        return resultado
    except Exception as exc:
        logger.error(f"[BACKUP TASK] Error crítico ejecutando respaldo: {exc}")
        return {'status': 'error', 'error': str(exc)}


# Alias de compatibilidad hacia atrás
task_ejecutar_backup_dual_gdrive = task_ejecutar_respaldo_programado





