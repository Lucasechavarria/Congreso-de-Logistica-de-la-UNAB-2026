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
            default=10,
            help='Cantidad de certificados a procesar en cada tanda (por defecto: 10)'
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
            default=2.0,
            help='Segundos de pausa entre cada envío individual de email para evitar rate-limits (por defecto: 2.0)'
        )
        parser.add_argument(
            '--pausa-lote',
            type=float,
            default=4.0,
            help='Segundos de pausa entre tandas sucesivas (por defecto: 4.0)'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        forzar = options['forzar']
        delay = options['delay']
        pausa_lote = options['pausa_lote']

        ahora_local = timezone.localtime(timezone.now())
        self.stdout.write(self.style.NOTICE(f"[CERTIFICADOS] Hora oficial actual: {ahora_local.strftime('%Y-%m-%d %H:%M:%S')} (GMT-3)"))

        if not forzar and ahora_local.hour < 18:
            self.stdout.write(self.style.WARNING(
                f"[BLOQUEO DE SEGURIDAD] La hora actual ({ahora_local.strftime('%H:%M:%S')}) es anterior a las 18:00 hs oficial.\n"
                f"El envío de certificados está programado para después de las 18 hs.\n"
                f"Si deseás omitir esta restricción para pruebas o despacho anticipado, ejecutá con --forzar."
            ))
            return

        total_pendientes = Certificado.objects.filter(email_enviado=False).count()
        if total_pendientes == 0:
            self.stdout.write(self.style.SUCCESS("[CERTIFICADOS] No hay certificados pendientes de envío."))
            return

        self.stdout.write(self.style.NOTICE(
            f"[CERTIFICADOS] Total pendientes: {total_pendientes} | Lote: {batch_size} | Delay: {delay}s"
        ))

        total_procesados = 0
        total_errores = 0

        while True:
            lote = list(Certificado.objects.filter(email_enviado=False).order_by('id')[:batch_size])
            if not lote:
                break

            self.stdout.write(f"\n--- Procesando tanda de {len(lote)} certificados ---")

            for idx, cert in enumerate(lote):
                destinatario = getattr(cert.asistente, 'email', '') or f"Asistente #{cert.asistente_id}"
                tipo_display = cert.get_tipo_certificado_display()
                try:
                    result = send_certificate_email(cert)
                    success = result[0] if isinstance(result, tuple) else bool(result)
                    if success:
                        total_procesados += 1
                        self.stdout.write(self.style.SUCCESS(f"  [OK] Enviado a {destinatario} ({tipo_display})"))
                    else:
                        total_errores += 1
                        motivo = result[1] if isinstance(result, tuple) and len(result) > 1 else "Fallo SMTP"
                        self.stdout.write(self.style.ERROR(f"  [ERROR] Falló envío a {destinatario}: {motivo}"))
                except Exception as exc:
                    total_errores += 1
                    self.stdout.write(self.style.ERROR(f"  [ERROR CRÍTICO] {destinatario}: {exc}"))

                if delay > 0 and idx < len(lote) - 1:
                    time.sleep(delay)

            restantes = Certificado.objects.filter(email_enviado=False).count()
            self.stdout.write(f"Estado: {total_procesados} enviados | {total_errores} errores | {restantes} restantes")

            if restantes > 0 and pausa_lote > 0:
                time.sleep(pausa_lote)

        self.stdout.write(self.style.SUCCESS(
            f"\n[FINALIZADO] Procesamiento de certificados completado.\n"
            f"Total enviados con éxito: {total_procesados} | Total errores: {total_errores}"
        ))
