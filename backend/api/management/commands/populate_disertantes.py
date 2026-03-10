
from django.core.management.base import BaseCommand
from api.models import Disertante
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Pobla la base de datos con disertantes usando los archivos de media/ponencias'

    def handle(self, *args, **options):
        base_path = os.path.join(settings.BASE_DIR, 'media', 'ponencias')
        archivos = [f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, f))]
        ejemplo_tema = 'Título de la Presentación'
        ejemplo_bio = 'Descripción de ejemplo del disertante.'
        count = 0
        for archivo in archivos:
            nombre_base = os.path.splitext(archivo)[0]
            nombre = ' '.join([w.capitalize() for w in nombre_base.split('_')])
            foto_url = f'ponencias/{archivo}'
            if not Disertante.objects.filter(nombre=nombre).exists():
                Disertante.objects.create(
                    nombre=nombre,
                    bio=ejemplo_bio,
                    foto_url=foto_url,
                    tema_presentacion=ejemplo_tema
                )
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Disertante creado: {nombre}'))
            else:
                self.stdout.write(self.style.WARNING(f'Disertante ya existe: {nombre}'))
        self.stdout.write(self.style.SUCCESS(f'Total de disertantes procesados: {count}'))
