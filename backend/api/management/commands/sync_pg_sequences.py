from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Sincroniza las secuencias autoincrementales de PostgreSQL con el MAX(id) actual de cada tabla para evitar errores IntegrityError (llaves duplicadas)."

    def handle(self, *args, **options):
        if connection.vendor != 'postgresql':
            self.stdout.write(self.style.WARNING(
                f"El motor de base de datos actual es '{connection.vendor}'. "
                "La sincronización de secuencias con setval() aplica exclusivamente a PostgreSQL."
            ))
            return

        tables_to_sync = [
            'api_programa',
            'api_programa_disertantes',
            'api_disertante',
            'api_postulaciondisertante',
            'api_asistente',
            'api_inscripcion',
            'api_inscripcionprensa',
            'api_empresa',
            'api_certificado',
            'api_edicion',
            'django_admin_log',
        ]

        self.stdout.write(self.style.MIGRATE_HEADING("Iniciando sincronización de secuencias en PostgreSQL..."))

        synced_count = 0
        with connection.cursor() as cursor:
            for table in tables_to_sync:
                try:
                    # Verificar si la tabla existe en la base de datos
                    cursor.execute(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);",
                        [table]
                    )
                    exists = cursor.fetchone()[0]
                    if not exists:
                        self.stdout.write(f"  [OMITIDA] Tabla '{table}' no existe en este esquema.")
                        continue

                    # Sincronizar secuencia
                    query = f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table}', 'id'),
                            COALESCE((SELECT MAX(id) FROM {table}), 1)
                        );
                    """
                    cursor.execute(query)
                    res = cursor.fetchone()
                    new_val = res[0] if res else 'OK'
                    self.stdout.write(self.style.SUCCESS(f"  [OK] '{table}': secuencia sincronizada en valor {new_val}."))
                    synced_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  [ERROR] Al sincronizar '{table}': {e}"))

        self.stdout.write(self.style.SUCCESS(f"\nSincronización completada exitosamente ({synced_count} tablas actualizadas)."))
