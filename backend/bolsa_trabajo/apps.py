from django.apps import AppConfig


class BolsaTrabajoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bolsa_trabajo'
    def ready(self):
        import bolsa_trabajo.signals
