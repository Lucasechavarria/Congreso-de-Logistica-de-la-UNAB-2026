import logging
from typing import Tuple, Dict, Any
from django.db import transaction
from django.utils import timezone
from .models import Inscripcion, Certificado, Empresa, Asistente, Edicion
from .email import send_certificate_email, send_empresa_confirmation_email

logger = logging.getLogger('django.services')

def confirm_asistencia(inscripcion: Inscripcion) -> Tuple[Certificado, bool]:
    """
    Servicio transaccional para confirmar la asistencia de un participante,
    generar su certificado e iniciar el proceso de envío de email de confirmación.
    Retorna una tupla (certificado, email_success).
    """
    with transaction.atomic():
        inscripcion.asistencia_confirmada = True
        inscripcion.fecha_confirmacion = timezone.now()
        inscripcion.save()

        # Crear u obtener el certificado de asistencia asociado a la edición específica
        certificado, created = Certificado.objects.get_or_create(
            asistente=inscripcion.asistente,
            edicion=inscripcion.edicion,
            tipo_certificado=Certificado.TipoCertificado.ASISTENCIA
        )
        
        # Encolar la generación y el envío del certificado asíncronamente (Celery)
        from .tasks import task_generar_y_enviar_certificado
        transaction.on_commit(lambda: task_generar_y_enviar_certificado.delay(certificado.id))
        email_success = True

        return certificado, email_success


def create_empresa_and_notify(data: Dict[str, Any]) -> Tuple[Empresa, bool]:
    """
    Servicio transaccional para procesar el registro de una empresa
    y notificarla por email de manera segura.
    Retorna una tupla (empresa, email_success).
    """
    from .serializers import EmpresaSerializer
    
    with transaction.atomic():
        # Validar y serializar la entrada usando el validador estricto de DRF
        serializer = EmpresaSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        empresa = serializer.save()
        
        # Enviar correo de confirmación de registro
        email_success = False
        try:
            email_success = send_empresa_confirmation_email(empresa)
        except Exception as e:
            logger.error(f"[Services] Error al enviar correo de bienvenida a empresa {empresa.nombre_empresa}: {str(e)}")
            
        return empresa, email_success


def _upsert_detalles(asistente: Asistente, data: dict) -> None:
    """
    Persiste o actualiza los detalles específicos del perfil del asistente.
    """
    from .models import Asistente, DetalleEstudiante, DetalleDocente, DetalleProfesional, DetalleGrupo
    
    profile_type = asistente.profile_type
    if profile_type in [Asistente.ProfileType.STUDENT, Asistente.ProfileType.GRADUADO]:
        DetalleEstudiante.objects.update_or_create(
            asistente=asistente,
            defaults={
                'is_unab_student': data.get('is_unab_student') or False,
                'institution': data.get('institution'),
                'career': data.get('career'),
                'year_of_study': data.get('year_of_study'),
            }
        )
    elif profile_type == Asistente.ProfileType.TEACHER:
        DetalleDocente.objects.update_or_create(
            asistente=asistente,
            defaults={
                'institution': data.get('institution'),
                'career_taught': data.get('career_taught'),
            }
        )
    elif profile_type in [Asistente.ProfileType.PROFESSIONAL, Asistente.ProfileType.OTRO]:
        DetalleProfesional.objects.update_or_create(
            asistente=asistente,
            defaults={
                'work_area': data.get('work_area') if profile_type == Asistente.ProfileType.PROFESSIONAL else "Otro",
                'occupation': data.get('occupation'),
            }
        )
    elif profile_type == Asistente.ProfileType.GROUP_REPRESENTATIVE:
        DetalleGrupo.objects.update_or_create(
            asistente=asistente,
            defaults={
                'group_name': data.get('group_name'),
                'group_municipality': data.get('group_municipality'),
                'group_size': data.get('group_size') or 0,
            }
        )


def _register_integrantes(representante: Asistente, integrantes_data: list, edicion_activa: Edicion) -> list:
    """
    Registra secuencialmente a cada integrante del grupo y lo inscribe a la edición activa.
    """
    from .models import Asistente, Inscripcion
    fallos_miembros = []
    
    for miembro_data in integrantes_data:
        try:
            with transaction.atomic():
                m_dni = miembro_data.get('dni')
                m_email = miembro_data.get('email')
                
                if not m_dni and not m_email:
                    raise ValueError("Nombre, Email o DNI faltantes en integrante.")

                m_asistente = None
                if m_dni:
                    m_asistente = Asistente.objects.filter(dni=m_dni).first()
                if not m_asistente and m_email:
                    m_asistente = Asistente.objects.filter(email=m_email).first()
                
                m_profile = miembro_data.get('profile_type', Asistente.ProfileType.VISITOR)
                m_defaults = {
                    'first_name': miembro_data['first_name'],
                    'last_name': miembro_data['last_name'],
                    'email': m_email,
                    'dni': m_dni,
                    'phone': miembro_data.get('phone'),
                    'profile_type': m_profile,
                    'representante_grupo': representante,
                    'comision': miembro_data.get('comision') or representante.comision,
                    'terminos_aceptados': True,
                }

                if m_asistente:
                    for attr, value in m_defaults.items():
                        setattr(m_asistente, attr, value)
                    m_asistente.save()
                else:
                    m_asistente = Asistente.objects.create(**m_defaults)
                
                # Guardar detalles del integrante si aplica
                _upsert_detalles(m_asistente, {
                    'institution': miembro_data.get('institution'),
                    'career': miembro_data.get('career'),
                })

                # Vincular miembro a Edición Activa
                if edicion_activa:
                    Inscripcion.objects.get_or_create(asistente=m_asistente, edicion=edicion_activa)

        except Exception as e:
            fallos_miembros.append(f"{miembro_data.get('first_name', 'Fila')} - {str(e)}")

    if fallos_miembros:
        logger.warning(f"[Services] Errores en integrantes de grupo: {fallos_miembros}")
        
    return fallos_miembros


def _extract_detalles_data(validated_data: dict) -> dict:
    """Extrae y retorna los campos de detalle del payload validado."""
    return {
        'is_unab_student': validated_data.pop('is_unab_student', False),
        'institution': validated_data.pop('institution', None),
        'career': validated_data.pop('career', None),
        'year_of_study': validated_data.pop('year_of_study', None),
        'career_taught': validated_data.pop('career_taught', None),
        'work_area': validated_data.pop('work_area', None),
        'occupation': validated_data.pop('occupation', None),
        'group_name': validated_data.pop('group_name', None),
        'group_municipality': validated_data.pop('group_municipality', None),
        'group_size': validated_data.pop('group_size', 0)
    }


def _upsert_asistente_principal(validated_data: dict) -> Asistente:
    """Busca y actualiza un asistente existente por DNI o Email, o crea uno nuevo."""
    from .models import Asistente
    from rest_framework import serializers

    dni = validated_data.get('dni')
    email = validated_data.get('email')

    asistente = None
    if dni:
        asistente = Asistente.objects.filter(dni=dni).first()
    if not asistente and email:
        asistente = Asistente.objects.filter(email=email).first()

    if asistente:
        # Verificar que el email no pertenezca a otro participante distinto
        if email and Asistente.objects.filter(email=email).exclude(pk=asistente.pk).exists():
            raise serializers.ValidationError({
                "email": "El correo electrónico ingresado ya se encuentra registrado por otro participante."
            })
        for attr, value in validated_data.items():
            setattr(asistente, attr, value)
        asistente.save()
    else:
        if email and Asistente.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "email": "El correo electrónico ya se encuentra registrado por otro participante."
            })
        if dni and Asistente.objects.filter(dni=dni).exists():
            raise serializers.ValidationError({
                "dni": "El DNI ya se encuentra registrado por otro participante."
            })
        asistente = Asistente.objects.create(**validated_data)
    return asistente


def register_asistente_or_group(validated_data: dict, integrantes_data: list = None) -> Asistente:
    """
    Caso de Uso Principal: Registra a un asistente (o representante de grupo),
    crea su inscripción para la edición activa y sus respectivos integrantes.
    """
    from .models import Asistente, Edicion
    from .tasks import task_enviar_confirmacion_grupal, task_enviar_confirmacion_individual

    edicion_activa = Edicion.objects.filter(activa=True).first()
    if not edicion_activa:
        from rest_framework import serializers
        raise serializers.ValidationError({"edicion": "No hay una edición activa configurada en el sistema."})

    with transaction.atomic():
        detalles_data = _extract_detalles_data(validated_data)
        asistente = _upsert_asistente_principal(validated_data)

        # Registrar detalles del asistente
        _upsert_detalles(asistente, detalles_data)

        # Asignar propiedades dinámicas en memoria para la respuesta del serializer
        for attr, value in detalles_data.items():
            setattr(asistente, attr, value)

        from .email import send_individual_confirmation_email, send_group_confirmation_emails

        def _safe_dispatch_grupal(a_id: int = asistente.id) -> None:
            try:
                task_enviar_confirmacion_grupal.delay(a_id)
            except Exception as e:
                logger.warning(f"[Celery] Error encolando o Redis no disponible ({e}). Ejecutando fallback síncrono grupal...")
                try:
                    rep = Asistente.objects.get(id=a_id)
                    send_group_confirmation_emails(rep)
                except Exception as sync_err:
                    logger.error(f"[Fallback Sync] Error en envío grupal directo: {sync_err}")

        def _safe_dispatch_individual(a_id: int = asistente.id) -> None:
            try:
                task_enviar_confirmacion_individual.delay(a_id)
            except Exception as e:
                logger.warning(f"[Celery] Error encolando o Redis no disponible ({e}). Ejecutando fallback síncrono individual...")
                try:
                    asis = Asistente.objects.get(id=a_id)
                    send_individual_confirmation_email(asis)
                except Exception as sync_err:
                    logger.error(f"[Fallback Sync] Error en envío individual directo: {sync_err}")

        if asistente.profile_type == Asistente.ProfileType.GROUP_REPRESENTATIVE:
            if integrantes_data:
                fallos = _register_integrantes(asistente, integrantes_data, edicion_activa)
                if fallos:
                    asistente._fallos_miembros = fallos
            transaction.on_commit(_safe_dispatch_grupal)
        else:
            transaction.on_commit(_safe_dispatch_individual)

    return asistente


import unicodedata

def clean_unicode_text(text: Any, max_len: int | None = None) -> str:
    """
    Limpia y normaliza cadenas de texto para asegurar compatibilidad total
    con caracteres latinos (á, é, í, ó, ú, ñ, Ñ, ü, Ü), elimina espacios
    indeseados (como non-breaking spaces \\xa0) y trunca a max_len si es necesario.
    """
    if not text:
        return ""
    s = str(text)
    s = unicodedata.normalize('NFC', s)
    s = s.replace('\xa0', ' ').replace('\r', '').strip()
    if max_len and len(s) > max_len:
        s = s[:max_len].strip()
    return s


def sync_postulacion_a_disertante(postulacion) -> None:
    """
    Sincroniza una PostulacionDisertante aprobada hacia el modelo público Disertante y el Programa.
    Aislado por edición: si pertenece a la misma edición actualiza sus datos, si es de otra edición no la modifica.
    Completamente defensivo contra errores de caracteres especiales latinos, archivos faltantes o inconsistencias de DB.
    """
    from .models import Disertante, Edicion
    from .services_programa import crear_o_actualizar_programa_desde_postulacion
    
    try:
        edicion = postulacion.edicion or Edicion.objects.filter(activa=True).first()
        nombre = clean_unicode_text(postulacion.nombre_apellido, max_len=200) or "Disertante"
        empresa = clean_unicode_text(postulacion.empresa_institucion, max_len=255)
        bio = clean_unicode_text(postulacion.resumen_charla)
        tema = clean_unicode_text(postulacion.titulo_charla, max_len=255) or "Disertación"
        linkedin = clean_unicode_text(postulacion.linkedin, max_len=500)
        
        if postulacion.estado == 'APROBADO':
            disertantes = Disertante.objects.filter(nombre=nombre, edicion=edicion)
            if disertantes.exists():
                disertante = disertantes.first()
                disertante.empresa_institucion = empresa
                disertante.bio = bio
                disertante.tema_presentacion = tema
                disertante.linkedin = linkedin if linkedin else None
                if postulacion.foto_perfil:
                    try:
                        if hasattr(postulacion.foto_perfil, 'storage') and postulacion.foto_perfil.name:
                            if postulacion.foto_perfil.storage.exists(postulacion.foto_perfil.name):
                                disertante.foto = postulacion.foto_perfil
                            else:
                                logger.warning(f"Foto {postulacion.foto_perfil.name} no existe en almacenamiento. Omitiendo asignación.")
                        else:
                            disertante.foto = postulacion.foto_perfil
                    except Exception as e:
                        logger.warning(f"No se pudo asignar foto_perfil al disertante {nombre}: {e}")
                disertante.estado = 'APROBADO'
                disertante.save()
            else:
                disertante = Disertante(
                    nombre=nombre,
                    edicion=edicion,
                    empresa_institucion=empresa,
                    bio=bio,
                    tema_presentacion=tema,
                    linkedin=linkedin if linkedin else None,
                    estado='APROBADO'
                )
                if postulacion.foto_perfil:
                    try:
                        if hasattr(postulacion.foto_perfil, 'storage') and postulacion.foto_perfil.name:
                            if postulacion.foto_perfil.storage.exists(postulacion.foto_perfil.name):
                                disertante.foto = postulacion.foto_perfil
                            else:
                                logger.warning(f"Foto {postulacion.foto_perfil.name} no existe en almacenamiento. Omitiendo asignación.")
                        else:
                            disertante.foto = postulacion.foto_perfil
                    except Exception as e:
                        logger.warning(f"No se pudo asignar foto_perfil al crear disertante {nombre}: {e}")
                disertante.save()

            
            # Sincronizar automáticamente con el Programa de esa edición
            try:
                crear_o_actualizar_programa_desde_postulacion(postulacion, disertante)
            except Exception as e:
                logger.error(f"Error al sincronizar programa para disertante {nombre}: {e}")
        else:
            Disertante.objects.filter(nombre=nombre, edicion=edicion).update(estado='PENDIENTE')
    except Exception as e:
        logger.error(f"Error general en sync_postulacion_a_disertante para postulacion ID {getattr(postulacion, 'id', None)}: {e}", exc_info=True)


import re
import zipfile
import pandas as pd

MAX_EXCEL_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

def sanitize_cell_text(value: Any) -> str:
    """
    Sanitiza cadenas provenientes de celdas de Excel para evitar:
    1. Inyección de fórmulas CSV/Excel (=, +, -, @, \t, \r, \n, %).
    2. Inyección de código malicioso XSS / HTML tags.
    """
    if value is None or pd.isna(value):
        return ""
    
    val_str = str(value).strip()
    if not val_str:
        return ""

    # Protección contra CSV / Formula Injection
    if val_str.startswith(('=', '+', '-', '@', '\t', '\r', '\n', '%')):
        val_str = "'" + val_str

    # Protección contra XSS y tags HTML
    val_str = re.sub(r'<script.*?>.*?</script>', '', val_str, flags=re.DOTALL | re.IGNORECASE)
    val_str = re.sub(r'<[^>]*>', '', val_str)

    return val_str.strip()


def validar_archivo_excel_seguro(file_obj, max_size_mb: int = 5) -> None:
    """
    Realiza la validación estricta de seguridad pre-flight del archivo subido:
    1. Verifica que el tamaño no supere el límite (5 MB por defecto).
    2. Verifica extensión .xlsx o .xls.
    3. Inspecciona Magic Bytes (PK\x03\x04 para archivos .xlsx) para evitar archivos maliciosos camuflados.
    """
    max_bytes = max_size_mb * 1024 * 1024
    if hasattr(file_obj, 'size') and file_obj.size > max_bytes:
        raise ValueError(f"El archivo excede el tamaño máximo permitido de {max_size_mb}MB.")

    filename = getattr(file_obj, 'name', '').lower()
    if not (filename.endswith('.xlsx') or filename.endswith('.xls') or filename.endswith('.csv')):
        raise ValueError("Formato de archivo no soportado. Debe ser un documento de Excel (.xlsx) o CSV.")

    # Verificación de Magic Bytes para .xlsx (debe comenzar con la firma ZIP 'PK\x03\x04')
    if filename.endswith('.xlsx'):
        try:
            file_obj.seek(0)
            header_bytes = file_obj.read(4)
            file_obj.seek(0)
            if header_bytes and not header_bytes.startswith(b'PK\x03\x04'):
                raise ValueError("El archivo no es una planilla Excel .xlsx válida o contiene firma de contenido inválida.")
        except ValueError:
            raise
        except Exception as e:
            file_obj.seek(0)
            raise ValueError(f"Error al verificar la firma de seguridad del archivo: {str(e)}")


class PreacreditacionValidationError(Exception):
    """Excepción personalizada para errores de validación fila por fila en preacreditación."""
    def __init__(self, errores: list, total_filas: int):
        self.errores = errores
        self.detalles = errores
        self.total_filas = total_filas
        super().__init__(f"Se encontraron {len(errores)} error(es) de validación en la planilla.")


def procesar_archivo_preacreditacion_empresa(empresa: Empresa, file_obj) -> Dict[str, Any]:
    """
    Servicio de procesamiento seguro del archivo PREACREDITACION EMPRESAS.xlsx.
    Implementa una estrategia 'All-or-Nothing' (Todo o Nada):
    1. Fase 1: Inspecciona y valida el 100% de las filas sin tocar la DB, recolectando errores con número de fila, columna y mensaje.
    2. Si existen errores de validación, cancela el guardado completo y retorna los errores estructurados.
    3. Fase 2: Si 0 filas tienen error, ejecuta un bloque `transaction.atomic()` para persistir las filas limpias.
    """
    from .models import PersonalEmpresa

    # 1. Validación estricta de seguridad Pre-flight (Tamaño, Extensión, Magic Bytes)
    validar_archivo_excel_seguro(file_obj, max_size_mb=5)

    # 2. Lectura segura con pandas / openpyxl capturando archivos corruptos o malformados
    filename = getattr(file_obj, 'name', '').lower()
    try:
        file_obj.seek(0)
        if filename.endswith('.csv'):
            df = pd.read_csv(file_obj)
        else:
            df = pd.read_excel(file_obj, engine='openpyxl')
    except zipfile.BadZipFile:
        raise ValueError("El archivo Excel está corrupto o no se puede descomprimir de forma segura (BadZipFile).")
    except pd.errors.EmptyDataError:
        raise ValueError("El archivo subido está totalmente vacío.")
    except Exception as e:
        raise ValueError(f"Ocurrió un error al leer la planilla Excel: {str(e)}")

    if df is None or df.empty:
        raise ValueError("La planilla Excel no contiene filas de datos para procesar.")

    # 3. Normalización y verificación de encabezados contra la plantilla original
    def clean_header(col_name):
        c = str(col_name).strip().upper()
        return c.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')

    df.columns = [clean_header(col) for col in df.columns]

    col_nombre = next((c for c in df.columns if any(k in c for k in ['NOMBRE', 'FIRST NAME'])), None)
    col_apellido = next((c for c in df.columns if any(k in c for k in ['APELLIDO', 'LAST NAME'])), None)
    col_dni = next((c for c in df.columns if any(k in c for k in ['DNI', 'DOCUMENTO', 'IDENTIFICACION'])), None)
    col_cargo = next((c for c in df.columns if any(k in c for k in ['CARGO', 'PUESTO', 'ROL', 'FUNCION'])), None)
    col_email = next((c for c in df.columns if any(k in c for k in ['EMAIL', 'CORREO', 'MAIL'])), None)
    col_telefono = next((c for c in df.columns if any(k in c for k in ['TELEFONO', 'CELULAR', 'PHONE'])), None)

    if not col_nombre and not col_apellido and not col_dni:
        raise ValueError(
            "Los encabezados de la planilla no coinciden con la plantilla oficial 'PREACREDITACION EMPRESAS.xlsx'. "
            "Se requieren las columnas: Nombre, Apellido, DNI."
        )

    EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    
    errores_detallados = []
    filas_sanitizadas = []
    
    # Rastrear duplicados dentro del propio archivo
    dnis_en_archivo = {}
    emails_en_archivo = {}

    # --- FASE 1: VALIDACIÓN COMPLETA Y RECOLECCIÓN DE ERRORES (Pre-DB) ---
    for idx, row in df.iterrows():
        row_num = idx + 2  # Fila 1 es el encabezado de Excel
        
        nombre_raw = sanitize_cell_text(row[col_nombre]) if col_nombre and pd.notna(row[col_nombre]) else ""
        apellido_raw = sanitize_cell_text(row[col_apellido]) if col_apellido and pd.notna(row[col_apellido]) else ""
        dni_raw = sanitize_cell_text(row[col_dni]) if col_dni and pd.notna(row[col_dni]) else ""
        cargo_raw = sanitize_cell_text(row[col_cargo]) if col_cargo and pd.notna(row[col_cargo]) else ""
        email_raw = sanitize_cell_text(row[col_email]).lower() if col_email and pd.notna(row[col_email]) else ""
        telefono_raw = sanitize_cell_text(row[col_telefono]) if col_telefono and pd.notna(row[col_telefono]) else ""

        # Ignorar filas completamente vacías (ej: filas al final del Excel)
        if not nombre_raw and not apellido_raw and not dni_raw and not email_raw:
            continue

        # Manejo de Nombre y Apellido combinados
        if not apellido_raw and nombre_raw and ' ' in nombre_raw:
            parts = nombre_raw.split(' ', 1)
            nombre_raw = parts[0]
            apellido_raw = parts[1]

        # Validaciones de la fila
        if not nombre_raw:
            errores_detallados.append({
                "fila": row_num,
                "columna": "Nombre",
                "valor": nombre_raw,
                "mensaje": "El campo Nombre es obligatorio."
            })

        if not apellido_raw:
            errores_detallados.append({
                "fila": row_num,
                "columna": "Apellido",
                "valor": apellido_raw,
                "mensaje": "El campo Apellido es obligatorio."
            })

        dni_limpio = re.sub(r'\D', '', dni_raw)
        if len(dni_limpio) == 9 and dni_limpio.endswith('0'):
            dni_limpio = dni_limpio[:8]

        if not dni_limpio:
            errores_detallados.append({
                "fila": row_num,
                "columna": "DNI",
                "valor": dni_raw,
                "mensaje": "El DNI es obligatorio y debe contener caracteres numéricos válidos."
            })
        elif len(dni_limpio) < 7 or len(dni_limpio) > 8:
            errores_detallados.append({
                "fila": row_num,
                "columna": "DNI",
                "valor": dni_raw,
                "mensaje": f"El DNI '{dni_raw}' debe tener entre 7 y 8 dígitos numéricos."
            })
        elif dni_limpio in dnis_en_archivo:
            errores_detallados.append({
                "fila": row_num,
                "columna": "DNI",
                "valor": dni_limpio,
                "mensaje": f"DNI duplicado en el archivo (coincide con la fila {dnis_en_archivo[dni_limpio]})."
            })
        else:
            dnis_en_archivo[dni_limpio] = row_num

        if email_raw:
            if not EMAIL_REGEX.match(email_raw):
                errores_detallados.append({
                    "fila": row_num,
                    "columna": "Email",
                    "valor": email_raw,
                    "mensaje": f"El formato del correo electrónico '{email_raw}' es inválido."
                })
            elif email_raw in emails_en_archivo:
                errores_detallados.append({
                    "fila": row_num,
                    "columna": "Email",
                    "valor": email_raw,
                    "mensaje": f"Correo electrónico duplicado en el archivo (coincide con la fila {emails_en_archivo[email_raw]})."
                })
            else:
                emails_en_archivo[email_raw] = row_num

        filas_sanitizadas.append({
            "nombre": nombre_raw.title(),
            "apellido": apellido_raw.title(),
            "dni": dni_limpio,
            "cargo": cargo_raw,
            "email": email_raw,
            "telefono": telefono_raw
        })

    # SI HAY ERRORES EN CUALQUIER FILA, CANCELAR Y LANZAR EXCEPCIÓN ALL-OR-NOTHING
    if errores_detallados:
        raise PreacreditacionValidationError(errores=errores_detallados, total_filas=len(df))

    # --- FASE 2: GUARDADO EN BLOQUE TRANSACCIONAL ATÓMICO (All-or-Nothing) ---
    creados = 0
    actualizados = 0

    with transaction.atomic():
        for fila in filas_sanitizadas:
            personal_obj = None
            if fila['dni']:
                personal_obj = PersonalEmpresa.objects.filter(empresa=empresa, dni=fila['dni']).first()
            if not personal_obj and fila['email']:
                personal_obj = PersonalEmpresa.objects.filter(empresa=empresa, email=fila['email']).first()

            if personal_obj:
                personal_obj.nombre = fila['nombre']
                personal_obj.apellido = fila['apellido']
                if fila['dni']:
                    personal_obj.dni = fila['dni']
                if fila['cargo']:
                    personal_obj.cargo = fila['cargo']
                if fila['email']:
                    personal_obj.email = fila['email']
                if fila['telefono']:
                    personal_obj.telefono = fila['telefono']
                personal_obj.save()
                actualizados += 1
            else:
                PersonalEmpresa.objects.create(
                    empresa=empresa,
                    nombre=fila['nombre'],
                    apellido=fila['apellido'],
                    dni=fila['dni'],
                    cargo=fila['cargo'],
                    email=fila['email'],
                    telefono=fila['telefono']
                )
                creados += 1

        total_empresa = PersonalEmpresa.objects.filter(empresa=empresa).count()
        empresa.cantidad_representantes = total_empresa
        empresa.save(update_fields=['cantidad_representantes'])

    return {
        'total_filas': len(df),
        'creados': creados,
        'actualizados': actualizados,
        'total_procesados': creados + actualizados,
        'total_personal_empresa': total_empresa
    }






