from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.dispatch import receiver


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # Importación tardía para evitar problemas de carga circular
        pass

@receiver(connection_created)
def set_sql_ascii_encoding(sender, connection, **kwargs):
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("SET client_encoding TO 'SQL_ASCII'")
            # print("[INFO] DB connection forced to SQL_ASCII")
