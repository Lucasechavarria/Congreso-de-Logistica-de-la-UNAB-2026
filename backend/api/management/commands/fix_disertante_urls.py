from django.core.management.base import BaseCommand
from api.models import Disertante
import re


class Command(BaseCommand):
    help = 'Limpia y normaliza las URLs de fotos de los disertantes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar cambios sin aplicarlos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: No se aplicarán cambios'))
        
        disertantes = Disertante.objects.all()
        total = disertantes.count()
        modificados = 0
        
        self.stdout.write(f'\nProcesando {total} disertantes...\n')
        
        for disertante in disertantes:
            original_url = disertante.foto_url
            nueva_url = self.limpiar_url(original_url)
            
            if original_url != nueva_url:
                modificados += 1
                self.stdout.write(
                    f'\n{self.style.SUCCESS("✓")} {disertante.nombre} (ID: {disertante.id})'
                )
                self.stdout.write(f'  Original: {original_url or "(vacío)"}')
                self.stdout.write(f'  Nueva:    {nueva_url or "(vacío)"}')
                
                if not dry_run:
                    disertante.foto_url = nueva_url
                    disertante.save()
        
        if modificados == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ Todas las URLs ya están correctas'))
        else:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f'\n{modificados} de {total} disertantes necesitan corrección')
                )
                self.stdout.write(
                    self.style.WARNING('Ejecuta sin --dry-run para aplicar los cambios')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'\n✓ {modificados} de {total} disertantes actualizados')
                )
    
    def limpiar_url(self, url):
        """
        Limpia y normaliza una URL de foto.
        Retorna una URL válida o cadena vacía.
        """
        if not url:
            return ""
        
        url = url.strip()
        
        # Caso 1: Rutas absolutas mal formadas con path completo del servidor
        if "Congreso-UNAB/backend/media/" in url:
            # Extraer solo la parte de ponencias/archivo.png
            url = url.split("media/")[-1]
            return f"ponencias/{url.split('ponencias/')[-1]}"
        
        # Caso 2: Ya es una URL completa HTTPS
        if url.startswith("https://"):
            return url
        
        # Caso 3: URL HTTP - convertir a ruta relativa
        if url.startswith("http://"):
            # Extraer la parte después de /media/
            if "/media/" in url:
                return url.split("/media/")[-1]
            return url.replace("http://", "https://")
        
        # Caso 4: Rutas absolutas del servidor /media/
        if url.startswith("/media/"):
            return url[7:]  # Quitar /media/ del inicio
        
        # Caso 5: Rutas que empiezan con media/
        if url.startswith("media/"):
            return url[6:]  # Quitar media/ del inicio
        
        # Caso 6: Ya está en formato correcto ponencias/archivo.png
        if url.startswith("ponencias/"):
            return url
        
        # Caso 7: Solo el nombre del archivo
        if "/" not in url:
            return f"ponencias/{url}"
        
        # Default: devolver como está
        return url
