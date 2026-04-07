from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OfertaLaboral
from api.email import send_admin_postulation_alert

@receiver(post_save, sender=OfertaLaboral)
def notify_admin_new_offer(sender, instance, created, **kwargs):
    """
    Envía una notificación al administrador cuando se crea una nueva oferta laboral
    o cuando una existente pasa a estado PENDIENTE.
    """
    if created and instance.estado == 'PENDIENTE':
        try:
            send_admin_postulation_alert(instance, "OfertaLaboral")
        except Exception as e:
            print(f"[ERROR] Error al enviar notificación de nueva oferta: {e}")
