import time
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Certificado
from api.email import send_certificate_email

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Procesa y envía los certificados pendientes por lotes controlados con protección de horario (18:00 hs Argentina).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=5,
            help='Cantidad de certificados a procesar en cada tanda (por defecto: 5)'
        )
        parser.add_argument(
            '--forzar',
            action='store_true',
            default=False,
            help='Omitir la validación de las 18:00 hs oficial de Argentina (para pruebas o despacho manual)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Segundos de pausa entre cada envío individual de email para evitar rate-limits (por defecto: 1.0)'
        )
        parser.add_argument(
            '--pausa-lote',
            type=float,
            default=4.0,
            help='Segundos de pausa entre tandas sucesivas (por defecto: 4.0)'
        )
        parser.add_argument(
            '--reintentar-fallidos',
            action='store_true',
            default=False,
            help='Reintentar también certificados que tuvieron errores en intentos previos'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        forzar = options['forzar']
        delay = options['delay']
        pausa_lote = options['pausa_lote']
        reintentar_fallidos = options.get('reintentar_fallidos', False)

        ahora_local = timezone.localtime(timezone.now())
        self.stdout.write(self.style.NOTICE(f"[CERTIFICADOS] Hora oficial actual: {ahora_local.strftime('%Y-%m-%d %H:%M:%S')} (GMT-3)"))

        from api.scheduler import (
            es_horario_habilitado_certificados,
            acquire_certificate_queue_lock,
            reclamar_lote_certificados,
        )

        if not forzar and not es_horario_habilitado_certificados(ahora_local):
            self.stdout.write(self.style.WARNING(
                f"[BLOQUEO DE SEGURIDAD] La hora actual ({ahora_local.strftime('%H:%M:%S')}) es anterior a las 18:00 hs oficial.\n"
                f"El envío de certificados está programado para después de las 18 hs.\n"
                f"Si deseás omitir esta restricción para pruebas o despacho anticipado, ejecutá con --forzar."
            ))
            return

        from django.core.mail import get_connection
        from api.services import sincronizar_certificados_asistencia

        try:
            sincronizar_certificados_asistencia()
        except Exception as sync_err:
            logger.warning(f"[CERTIFICADOS CMD] Error sincronizando asistencias: {sync_err}")

        total_pendientes = Certificado.objects.filter(email_enviado=False).count()
        if total_pendientes == 0:
            self.stdout.write(self.style.SUCCESS("[CERTIFICADOS] No hay certificados pendientes de envío."))
            return

        self.stdout.write(self.style.NOTICE(
            f"[CERTIFICADOS] Total pendientes: {total_pendientes} | Lote: {batch_size} | Delay: {delay}s"
        ))

        total_procesados = 0
        total_errores = 0
        cursor_id = 0

        while True:
            with acquire_certificate_queue_lock() as lock_acquired:
                if not lock_acquired:
                    self.stdout.write(self.style.WARNING(
                        "  [PG LOCK] Otro proceso o la consola web tiene el bloqueo activo. Esperando 3s..."
                    ))
                    time.sleep(3.0)
                    continue

                lote = reclamar_lote_certificados(
                    batch_size=batch_size,
                    reintentar_fallidos=reintentar_fallidos,
                    after_id=cursor_id,
                    max_intentos_auto=None,
                )

                if not lote:
                    break

                self.stdout.write(f"\n--- Procesando tanda de {len(lote)} certificados ---")
                batch_start = time.monotonic()
                MAX_BATCH_SECONDS = 12.0

                smtp_conn = None
                smtp_open_failed = False
                try:
                    smtp_conn = get_connection(fail_silently=False)
                    smtp_conn.open()
                except Exception:
                    smtp_conn = None
                    smtp_open_failed = True

                try:
                    for idx, cert in enumerate(lote):
                        if (time.monotonic() - batch_start) >= MAX_BATCH_SECONDS:
                            self.stdout.write(self.style.WARNING("  [TIEMPO] Límite seguro por tanda alcanzado (12s). Continuando en la siguiente tanda..."))
                            break

                        if cert.id > cursor_id:
                            cursor_id = cert.id

                        destinatario = getattr(cert.asistente, 'email', '') or f"Asistente #{cert.asistente_id}"
                        tipo_display = cert.get_tipo_certificado_display()
                        try:
                            result = send_certificate_email(cert, connection=smtp_conn)
                            success = result[0] if isinstance(result, tuple) else bool(result)
                            if success:
                                total_procesados += 1
                                self.stdout.write(self.style.SUCCESS(f"  [OK] Enviado a {destinatario} ({tipo_display})"))
                            else:
                                total_errores += 1
                                motivo = result[1] if isinstance(result, tuple) and len(result) > 1 else "Fallo SMTP"
                                self.stdout.write(self.style.ERROR(f"  [ERROR] Falló envío a {destinatario}: {motivo}"))
                                es_error_smtp = "Fallo en PDF o SMTP" in str(motivo)
                                if smtp_open_failed and es_error_smtp:
                                    break
                                if (
                                    smtp_conn is not None
                                    and es_error_smtp
                                    and idx < len(lote) - 1
                                    and (time.monotonic() - batch_start) < MAX_BATCH_SECONDS
                                ):
                                    try:
                                        smtp_conn.close()
                                        smtp_conn.open()
                                    except Exception:
                                        smtp_conn = None
                                        break
                        except Exception as exc:
                            total_errores += 1
                            self.stdout.write(self.style.ERROR(f"  [ERROR CRÍTICO] {destinatario}: {exc}"))
                            if smtp_open_failed:
                                break

                        if delay > 0 and idx < len(lote) - 1:
                            if (time.monotonic() - batch_start + delay) < MAX_BATCH_SECONDS:
                                time.sleep(delay)
                finally:
                    if smtp_conn is not None:
                        try:
                            smtp_conn.close()
                        except Exception:
                            pass

            if reintentar_fallidos:
                restantes_sin_intentar = Certificado.objects.filter(email_enviado=False, id__gt=cursor_id).count()
            else:
                restantes_sin_intentar = Certificado.objects.filter(email_enviado=False, intentos=0).count()
            restantes_totales = Certificado.objects.filter(email_enviado=False).count()
            self.stdout.write(f"Estado: {total_procesados} enviados | {total_errores} errores | {restantes_totales} pendientes totales ({restantes_sin_intentar} por intentar)")

            if restantes_sin_intentar > 0 and pausa_lote > 0:
                time.sleep(pausa_lote)

        self.stdout.write(self.style.SUCCESS(
            f"\n[FINALIZADO] Procesamiento de certificados completado.\n"
            f"Total enviados con éxito: {total_procesados} | Total errores: {total_errores}"
        ))
