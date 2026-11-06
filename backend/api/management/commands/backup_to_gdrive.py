import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.gdrive_backup_service import ejecutar_backup_completo, generar_paquete_backup

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ejecuta el respaldo dual del Congreso (Excel + Base de Datos) y lo sube a Google Drive (Personal e Institucional).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--solo-local',
            action='store_true',
            default=False,
            help='Genera únicamente el archivo .zip local en backend/backups/ sin subir a Google Drive'
        )

    def handle(self, *args, **options):
        ahora_local = timezone.localtime(timezone.now())
        self.stdout.write(self.style.NOTICE(
            f"[RESPALDO] Iniciando proceso a las {ahora_local.strftime('%Y-%m-%d %H:%M:%S')} (GMT-3)..."
        ))

        if options['solo_local']:
            try:
                zip_path, zip_name, size_bytes = generar_paquete_backup()
                self.stdout.write(self.style.SUCCESS(
                    f"[OK] Archivo local generado exitosamente: {zip_path} ({round(size_bytes / 1024, 1)} KB)"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[ERROR] Falló la generación local: {e}"))
            return

        resultado = ejecutar_backup_completo()
        if resultado.get('status') == 'ok':
            self.stdout.write(self.style.SUCCESS(
                f"[OK] Respaldo finalizado: {resultado.get('archivo')}\n"
                f"Reporte:\n{resultado.get('reporte')}"
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f"[{resultado.get('status').upper()}] {resultado.get('message')}"
            ))

