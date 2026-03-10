import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from api.models import Empresa


class Command(BaseCommand):
    help = 'Importar empresas desde los logos hardcodeados del frontend'

    def add_arguments(self, parser):
        parser.add_argument(
            '--frontend-path',
            type=str,
            default='/home/daro/Documentos/FolKode Group/proyectos/congreso/Congreso-UNAB/client',
            help='Ruta al directorio del frontend (client)',
        )

    def handle(self, *args, **options):
        frontend_path = options['frontend_path']
        
        # Lista de empresas extraída del archivo logos.ts + empresas faltantes encontradas
        empresas_data = [
            {"nombre": "Aeronova", "logo_path": "/images/logos/AERONOVA.jpg"},
            {"nombre": "ARLOG", "logo_path": "/images/logos/ARLOG.png"},
            {"nombre": "Cargo", "logo_path": "/images/logos/LOGO-CARGO.png"},
            {"nombre": "CHAGA", "logo_path": "/images/logos/CHAGA.png"},
            {"nombre": "CityOne", "logo_path": "/images/logos/CITYONE.png"},
            {"nombre": "Conwork", "logo_path": "/images/logos/CONWORK.jpg"},
            {"nombre": "EAL Green", "logo_path": "/images/logos/EAL-GREEN.png"},
            {"nombre": "eTruck", "logo_path": "/images/logos/ETRUCK.png"},
            {"nombre": "ElectriTruck", "logo_path": "/images/logos/ELECTRITRUCK.jpeg"},
            {"nombre": "Escuela de Choferes", "logo_path": "/images/logos/ESCUELA-CHOFERES.png"},
            {"nombre": "Folkode Group", "logo_path": "/images/logos/Folkode_Group.webp"},
            {"nombre": "Genba Kaizen", "logo_path": "/images/logos/GENBA-KAIZEN.jpeg"},
            {"nombre": "GLI", "logo_path": "/images/logos/GLI.jpg"},
            {"nombre": "Gruas Golisano", "logo_path": "/images/logos/GRUAS-GOLISANO.png"},
            {"nombre": "ICI", "logo_path": "/images/logos/ICI.png"},
            {"nombre": "KMD Logística", "logo_path": "/images/logos/KMD.png"},
            {"nombre": "KPI Consulting", "logo_path": "/images/logos/KPI-CONSULTING.png"},
            {"nombre": "La Postal", "logo_path": "/images/logos/LA-POSTAL.png"},
            {"nombre": "Logística E-LECE", "logo_path": "/images/logos/ELECE-LOGISTICA.png"},
            {"nombre": "Logística Garpic", "logo_path": "/images/logos/LOGISTICA-GARPIC.png"},
            {"nombre": "M-RRHH", "logo_path": "/images/logos/M-RRHH.jpeg"},
            {"nombre": "Miniscenics", "logo_path": "/images/logos/MINISCENICS.jpeg"},
            {"nombre": "Muvon", "logo_path": "/images/logos/MUVON.png"},
            {"nombre": "N&G Transportes", "logo_path": "/images/logos/NYG-TRANSPORTES.PNG"},
            {"nombre": "Núcleo Logístico", "logo_path": "/images/logos/NUCLEO-LOGISTICO.jpeg"},
            {"nombre": "Performance Lube", "logo_path": "/images/logos/PERFORMANCE-LUBE.png"},
            {"nombre": "PYB", "logo_path": "/images/logos/PYB.jpg"},
            {"nombre": "Rasta", "logo_path": "/images/logos/RASTA.png"},
            {"nombre": "Red Logística", "logo_path": "/images/logos/RED-LOGISTICA.webp"},
            {"nombre": "Red Parques Digital", "logo_path": "/images/logos/RED-PARQUES.png"},
            {"nombre": "Shiaffer", "logo_path": "/images/logos/SHIAFFER.png"},
            {"nombre": "StarGPS", "logo_path": "/images/logos/STARGPS.png"},
            {"nombre": "Surfrigo", "logo_path": "/images/logos/SURFRIGO.jpeg"},
            {"nombre": "Traden", "logo_path": "/images/logos/TRADEN.png"},
            {"nombre": "Transporte Dominguez", "logo_path": "/images/logos/TRANSPORTE-DOMINGUEZ.png"},
            {"nombre": "UCASAL", "logo_path": "/images/logos/UCASAL.png"},
            {"nombre": "UNLaM", "logo_path": "/images/logos/UNLAM.png"},
            {"nombre": "UNLP", "logo_path": "/images/logos/UNLP.png"},
            {"nombre": "UNLZ", "logo_path": "/images/logos/UNLZ.png"},
            {"nombre": "UNS", "logo_path": "/images/logos/UNS.jpg"},
            {"nombre": "UPE", "logo_path": "/images/logos/UPE.png"},
            {"nombre": "UTN", "logo_path": "/images/logos/UTN.png"},
            {"nombre": "VDM Logistics", "logo_path": "/images/logos/VDM-LOGISTICS.jpg"},
            {"nombre": "Velox", "logo_path": "/images/logos/VELOX.jpeg"},
            {"nombre": "VIMA", "logo_path": "/images/logos/VIMA.png"},
            {"nombre": "VOS", "logo_path": "/images/logos/VOS.jpeg"},
            {"nombre": "Xperts", "logo_path": "/images/logos/XPERTS.jpeg"},
            {"nombre": "Zento", "logo_path": "/images/logos/Zento.jpg"},
        ]

        for empresa_data in empresas_data:
            nombre = empresa_data['nombre']
            logo_path = empresa_data['logo_path']
            
            # Verificar si la empresa ya existe
            empresa, created = Empresa.objects.get_or_create(
                nombre_empresa=nombre,
                defaults={
                    'nombre_contacto': f'Contacto {nombre}',
                    'email_contacto': f'contacto@{nombre.lower().replace(" ", "")}.com',
                    'celular_contacto': '000000000',
                    'cargo_contacto': 'Representante',
                    'participacion_opciones': 'Sponsor',
                }
            )
            
            if created or not empresa.logo:
                # Intentar copiar el logo desde el frontend
                full_logo_path = os.path.join(frontend_path, 'public', logo_path.lstrip('/'))
                
                if os.path.exists(full_logo_path):
                    try:
                        with open(full_logo_path, 'rb') as logo_file:
                            logo_content = logo_file.read()
                            # Extraer el nombre del archivo
                            logo_filename = os.path.basename(logo_path)
                            empresa.logo.save(
                                logo_filename,
                                ContentFile(logo_content),
                                save=True
                            )
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ {nombre}: Logo importado desde {full_logo_path}')
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'✗ {nombre}: Error al importar logo - {e}')
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ {nombre}: Logo no encontrado en {full_logo_path}')
                    )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'↻ {nombre}: Ya existe con logo')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Proceso completado. Total empresas: {Empresa.objects.count()}')
        )