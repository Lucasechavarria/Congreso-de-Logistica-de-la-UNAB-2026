import os
from django.core.management.base import BaseCommand
from api.backup_service import generar_paquete_backup, ejecutar_respaldo_programado


class Command(BaseCommand):
    help = (
        "Genera un paquete unificado de respaldo del sistema (.zip) conteniendo "
        "base de datos relacional (PostgreSQL SQL / SQLite), volcado portable JSON "
        "y planilla consolidada Excel (.xlsx). Opcionalmente envía copia por correo."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--enviar-email',
            action='store_true',
            help='Envía el paquete de respaldo generado por correo a las casillas configuradas.',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Dirección de correo específica adicional a la cual despachar el respaldo.',
        )
        parser.add_argument(
            '--solo-generar',
            action='store_true',
            help='Solo genera el archivo ZIP en disco e imprime su ruta absoluta.',
        )

    def handle(self, *args, **options):
        enviar_email = options.get('enviar_email')
        email_especifico = options.get('email')
        solo_generar = options.get('solo_generar')

        self.stdout.write(self.style.NOTICE("Iniciando proceso unificado de respaldo del sistema..."))

        if solo_generar or not (enviar_email or email_especifico):
            zip_path, zip_name, size_bytes = generar_paquete_backup()
            size_kb = size_bytes / 1024
            self.stdout.write(self.style.SUCCESS(f"✓ Respaldo generado con éxito: {zip_path} ({size_kb:.1f} KB)"))
            self.stdout.write(f"  Archivo: {zip_name}")
            return

        destinos = [email_especifico] if email_especifico else None
        res = ejecutar_respaldo_programado(destinos_forzados=destinos)

        if res.get('ok'):
            self.stdout.write(self.style.SUCCESS(f"✓ Respaldo completado exitosamente: {res.get('archivo')}"))
            if res.get('emails_enviados'):
                self.stdout.write(self.style.SUCCESS(f"✓ Enviado por correo a: {', '.join(res.get('emails_enviados'))}"))
            self.stdout.write("\nLogs de la ejecución:")
            for line in res.get('logs', []):
                self.stdout.write(f"  {line}")
        else:
            self.stdout.write(self.style.ERROR(f"✗ Error durante la ejecución del respaldo: {res.get('error')}"))
            for line in res.get('logs', []):
                self.stdout.write(f"  {line}")
