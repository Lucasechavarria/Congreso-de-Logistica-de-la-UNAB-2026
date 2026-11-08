from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        try:
            from .scheduler import iniciar_scheduler_en_segundo_plano
            iniciar_scheduler_en_segundo_plano()
        except Exception:
            pass
