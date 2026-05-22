import os
import sys
import django
import pandas as pd
import re

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Asistente, Edicion, Inscripcion, DetalleEstudiante, DetalleDocente
from django.utils import timezone
from django.db import transaction

def limpiar_email(email):
    if not isinstance(email, str):
        return ""
    email = email.strip().lower()
    # Reemplazar eñes y tildes comunes antes del @
    email = email.replace("ñ", "n")
    email = email.replace("á", "a")
    email = email.replace("é", "e")
    email = email.replace("í", "i")
    email = email.replace("ó", "o")
    email = email.replace("ú", "u")
    # Reemplazar doble punto en el dominio
    email = email.replace("..com", ".com")
    # Reemplazar comas por puntos
    email = email.replace(",", ".")
    # Si no tiene .com al final, pero termina en gmail, agregar .com
    if email.endswith("@gmail"):
        email = email + ".com"
    elif "@gmail" in email and not email.endswith(".com") and not email.endswith(".ar"):
        if email.split("@")[1] == "gmail":
            email = email + ".com"
    return email

def limpiar_dni(dni):
    if pd.isna(dni):
        return None
    dni_str = str(dni).strip()
    dni_limpio = re.sub(r'\D', '', dni_str)
    if len(dni_limpio) == 9 and dni_limpio.endswith('0'):
        dni_limpio = dni_limpio[0:8]
    return dni_limpio

def run():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../Congreso_de_Logística_2026.xlsx')
    
    if not os.path.exists(excel_path):
        print(f"Error: El archivo Excel no existe en {excel_path}")
        return

    print("Cargando archivo Excel...")
    df = pd.read_excel(excel_path)
    df.columns = df.columns.str.strip()
    
    print(f"Se encontraron {len(df)} registros en el Excel.")
    
    try:
        edicion_2026 = Edicion.objects.get(anio=2026, activa=True)
        print(f"Edición activa encontrada: {edicion_2026}")
    except Edicion.DoesNotExist:
        print("Error: No se encontró la edición activa 2026. Asegúrate de ejecutar setup_editions.py primero.")
        return

    creados = 0
    actualizados = 0
    inscritos = 0
    
    for idx, row in df.iterrows():
        try:
            # Extraer campos
            raw_nombre = str(row.get('Nombre', '')).strip()
            raw_apellido = str(row.get('apellido', '')).strip()
            raw_email = str(row.get('EMAIL', '')).strip()
            raw_dni = row.get('DNI', '')
            raw_telefono = str(row.get('TELEFONO', '')).strip()
            raw_perfil = str(row.get('PERFIL', '')).strip().lower()
            raw_institucion = str(row.get('INSTITUCION', '')).strip()
            raw_carrera = str(row.get('CARRERA', '')).strip()
            
            # Formatear email y dni
            email = limpiar_email(raw_email)
            dni = limpiar_dni(raw_dni)
            
            if not dni:
                print(f"[{idx}] Saltando registro debido a DNI ausente o inválido.")
                continue
            
            # Inversión de campos Nombre / Apellido a partir de la fila 40 (índice 39)
            if idx >= 39:
                first_name = raw_apellido
                last_name = raw_nombre
            else:
                first_name = raw_nombre
                last_name = raw_apellido
                
            # Limpiar dobles espacios en nombres y apellidos
            first_name = " ".join(first_name.split())
            last_name = " ".join(last_name.split())
            
            # Limpiar teléfono
            phone = raw_telefono if raw_telefono else None
            
            # Mapear perfil
            if "docente" in raw_perfil:
                profile_type = Asistente.ProfileType.TEACHER
            else:
                profile_type = Asistente.ProfileType.STUDENT
                
            # Buscar asistente existente por DNI o por Email
            asistente = None
            asistente_by_dni = Asistente.objects.filter(dni=dni).first()
            asistente_by_email = Asistente.objects.filter(email=email).first()
            
            if asistente_by_dni:
                asistente = asistente_by_dni
                # Actualizar email si cambió y no colisiona
                if asistente.email != email:
                    if not Asistente.objects.filter(email=email).exclude(id=asistente.id).exists():
                        asistente.email = email
            elif asistente_by_email:
                asistente = asistente_by_email
                # Actualizar DNI si cambió y no colisiona
                if asistente.dni != dni:
                    if not Asistente.objects.filter(dni=dni).exclude(id=asistente.id).exists():
                        asistente.dni = dni
            
            with transaction.atomic():
                is_new = False
                if asistente is None:
                    asistente = Asistente(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        dni=dni,
                        phone=phone,
                        profile_type=profile_type
                    )
                    is_new = True
                else:
                    # Actualizar datos del asistente
                    asistente.first_name = first_name
                    asistente.last_name = last_name
                    asistente.phone = phone
                    asistente.profile_type = profile_type
                
                asistente.save()
                
                if is_new:
                    creados += 1
                else:
                    actualizados += 1
                    
                # Crear o actualizar Detalles de Perfil
                if profile_type == Asistente.ProfileType.TEACHER:
                    detalle, _ = DetalleDocente.objects.get_or_create(asistente=asistente)
                    detalle.institution = raw_institucion or "ISDFYT 83"
                    detalle.career_taught = raw_carrera or "LOGISTICA"
                    detalle.save()
                else:
                    detalle, _ = DetalleEstudiante.objects.get_or_create(asistente=asistente)
                    detalle.institution = raw_institucion or "ISDFYT 83"
                    detalle.career = raw_carrera or "LOGISTICA"
                    detalle.is_unab_student = False
                    detalle.save()
                    
                # Crear inscripción a la edición 2026 activa
                inscripcion, ins_created = Inscripcion.objects.get_or_create(
                    asistente=asistente,
                    edicion=edicion_2026,
                    defaults={'asistencia_confirmada': False}
                )
                if ins_created:
                    inscritos += 1
                    
        except Exception as e:
            print(f"Error procesando fila {idx} (Nombre: {raw_nombre}, DNI: {raw_dni}): {e}")
            
    print("\n--- Resultados de la Importación Masiva ---")
    print(f"Asistentes Nuevos Creados: {creados}")
    print(f"Asistentes Existentes Actualizados: {actualizados}")
    print(f"Nuevas Inscripciones creadas para la Edición 2026: {inscritos}")
    print("------------------------------------------")

if __name__ == "__main__":
    run()
