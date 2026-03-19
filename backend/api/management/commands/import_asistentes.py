import re
import os
from typing import List, Any, Optional
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Asistente, DetalleEstudiante, DetalleDocente, DetalleProfesional, DetalleGrupo

class Command(BaseCommand):
    help = 'Importa asistentes desde el archivo migrate_data.sql'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='migrate_data.sql',
            help='Ruta al archivo SQL de migración',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {file_path}'))
            return

        self.stdout.write(f'Leyendo {file_path}...')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex para capturar los valores de los INSERT INTO api_asistente
        # Estructura antigua: (id, nombre, apellido, email, dni, celular, institucion, cargo, tipo_perfil, fecha_registro, hash_qr, ya_ingreso, fecha_ingreso)
        insert_pattern = re.compile(r"INSERT INTO api_asistente.*?VALUES\s*(.*?);", re.DOTALL)
        values_pattern = re.compile(r"\((.*?)\)", re.DOTALL)

        matches = insert_pattern.findall(content)
        total_created = 0
        total_updated = 0
        total_errors = 0

        for match in matches:
            # Dividir por tuplas de valores
            value_tuples = values_pattern.findall(match)
            for tuple_str in value_tuples:
                try:
                    # Limpiar y dividir los valores (con cuidado por las comas dentro de strings)
                    # Una forma simple es usar un regex que capture strings entre comillas o NULL
                    # Ejemplo: 'Nombre', 'Apellido', 'email@test.com', '12345678', NULL, ...
                    parts: List[Optional[str]] = []
                    # Regex para capturar: 'valor' o NULL o números
                    for part in re.finditer(r"'(.*?)'|NULL|(\d+)", tuple_str):
                        val = part.group(0)
                        if val == 'NULL':
                            parts.append(None)
                        elif val.startswith("'"):
                            parts.append(val.strip("'"))
                        else:
                            parts.append(val)
                    
                    if len(parts) < 9:
                        continue

                    # Mapeo según estructura antigua:
                    # 0: id, 1: nombre, 2: apellido, 3: email, 4: dni, 5: celular, 6: institucion, 7: cargo, 8: tipo_perfil
                    
                    nombre = parts[1]
                    apellido = parts[2]
                    email = parts[3]
                    dni = parts[4]
                    celular = parts[5]
                    institucion = parts[6]
                    cargo = parts[7]
                    tipo_perfil_raw = parts[8]

                    if not email or not dni:
                        continue

                    # Mapear tipo de perfil al nuevo sistema
                    tipo_perfil = Asistente.ProfileType.VISITOR
                    if tipo_perfil_raw:
                        tp = tipo_perfil_raw.upper()
                        if 'ESTUDIANTE' in tp: tipo_perfil = Asistente.ProfileType.STUDENT
                        elif 'DOCENTE' in tp: tipo_perfil = Asistente.ProfileType.TEACHER
                        elif 'PROFESIONAL' in tp: tipo_perfil = Asistente.ProfileType.PROFESSIONAL
                        elif 'VISITANTE' in tp: tipo_perfil = Asistente.ProfileType.VISITOR

                    with transaction.atomic():
                        asistente, created = Asistente.objects.update_or_create(
                            dni=dni,
                            defaults={
                                'first_name': nombre,
                                'last_name': apellido,
                                'email': email,
                                'phone': celular,
                                'profile_type': tipo_perfil,
                                'terminos_aceptados': True,
                            }
                        )

                        # Crear detalles según el tipo
                        if tipo_perfil == Asistente.ProfileType.STUDENT:
                            DetalleEstudiante.objects.get_or_create(
                                asistente=asistente,
                                defaults={'institution': institucion, 'career': cargo}
                            )
                        elif tipo_perfil == Asistente.ProfileType.TEACHER:
                            DetalleDocente.objects.get_or_create(
                                asistente=asistente,
                                defaults={'institution': institucion, 'career_taught': cargo}
                            )
                        elif tipo_perfil == Asistente.ProfileType.PROFESSIONAL:
                            DetalleProfesional.objects.get_or_create(
                                asistente=asistente,
                                defaults={'work_area': institucion, 'occupation': cargo}
                            )

                        if created:
                            total_created += 1
                        else:
                            total_updated += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error procesando tupla: {e}'))
                    total_errors += 1

        self.stdout.write(self.style.SUCCESS(
            f'Migración completada: {total_created} creados, {total_updated} actualizados, {total_errors} errores.'
        ))
