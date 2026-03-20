from django.core.management.base import BaseCommand
from api.models import Edicion, Asistente, Inscripcion, Empresa, PostulacionDisertante, Disertante, InscripcionPrensa, Programa
from django.utils import timezone

class Command(BaseCommand):
    help = 'Inicializa las ediciones 2025 y 2026 y categoriza los datos existentes.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando configuración de ediciones...")
        
        # 1. Crear ediciones si no existen
        edicion_2025, created = Edicion.objects.get_or_create(
            anio=2025,
            defaults={'nombre': 'Congreso Logística 2025', 'activa': False}
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Creada Edición 2025."))
        
        edicion_2026, created = Edicion.objects.get_or_create(
            anio=2026,
            defaults={'nombre': 'Congreso Logística 2026', 'activa': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Creada Edición 2026 (Activa)."))
        else:
            # Asegurar que la 2026 sea la activa
            edicion_2026.activa = True
            edicion_2026.save()

        # 2. Migrar asistentes actuales a la edición 2025
        self.stdout.write("Migrando asistentes a la edición 2025...")
        asistentes = Asistente.objects.all()
        count_ins = 0
        for asistente in asistentes:
            if not Inscripcion.objects.filter(asistente=asistente, edicion=edicion_2025).exists():
                Inscripcion.objects.create(
                    asistente=asistente,
                    edicion=edicion_2025,
                    fecha_inscripcion=asistente.fecha_registro or timezone.now()
                )
                count_ins += 1
        self.stdout.write(self.style.SUCCESS(f"Se crearon {count_ins} inscripciones para la edición 2025."))

        # 3. Asignar edición 2025 a otros modelos que tengan edicion=None
        self.stdout.write("Asignando edición 2025 a registros huérfanos...")
        
        models_to_fix = [
            (Empresa, 'empresas'),
            (PostulacionDisertante, 'postulaciones'),
            (Disertante, 'disertantes'),
            (InscripcionPrensa, 'inscripciones prensa'),
            (Programa, 'programa')
        ]
        
        for model, label in models_to_fix:
            updated = model.objects.filter(edicion__isnull=True).update(edicion=edicion_2025)
            self.stdout.write(self.style.SUCCESS(f"Actualizados {updated} registros de {label}."))

        self.stdout.write(self.style.SUCCESS("Configuración finalizada con éxito."))
