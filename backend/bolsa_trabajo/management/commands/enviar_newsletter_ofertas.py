from django.core.management.base import BaseCommand
from bolsa_trabajo.tasks import enviar_newsletter_semanal

class Command(BaseCommand):
    help = 'Envía el newsletter semanal de ofertas laborales a los suscriptores'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando envío de newsletter semanal...')
        resultado = enviar_newsletter_semanal()
        self.stdout.write(self.style.SUCCESS(f'Resultado: {resultado}'))
