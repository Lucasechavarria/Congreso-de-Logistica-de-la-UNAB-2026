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
    registrar su certificado en cola para envío diferido por lotes (después de las 18 hs)
    y disparar de forma asíncrona el email de Confirmación de Asistencia inmediato.
    Retorna una tupla (certificado, email_success).
    """
    with transaction.atomic():
        inscripcion.asistencia_confirmada = True
        inscripcion.fecha_confirmacion = timezone.now()
        inscripcion.save()

        asistente = inscripcion.asistente

        # Determinar el tipo de certificado según la vinculación del participante
        tipo_cert = Certificado.TipoCertificado.ASISTENCIA
        if getattr(asistente, 'disertante_vinculado_id', None):
            tipo_cert = Certificado.TipoCertificado.DISERTANTE
        elif getattr(asistente, 'empresa_vinculada_id', None):
            tipo_cert = Certificado.TipoCertificado.EMPRESA

        # Crear u obtener el certificado asociado a la edición específica (queda pendiente: email_enviado=False)
        certificado, created = Certificado.objects.get_or_create(
            asistente=asistente,
            edicion=inscripcion.edicion,
            tipo_certificado=tipo_cert,
            defaults={'email_enviado': False}
        )

        # Encolar el envío del Email de Confirmación de Asistencia (liviano e inmediato).
        # El certificado queda en cola para ser emitido por lotes después de las 18:00 hs.
        from .tasks import task_enviar_confirmacion_asistencia
        from .email import send_attendance_confirmation_email

        def _safe_dispatch_confirmacion_asistencia(asist_id: int = asistente.id, insc_id: int = inscripcion.id) -> None:
            try:
                task_enviar_confirmacion_asistencia.delay(asist_id, insc_id)
            except Exception as e:
                logger.warning(f"[Celery] Error encolando confirmación de asistencia ({e}). Ejecutando fallback síncrono...")
                try:
                    a = Asistente.objects.get(id=asist_id)
                    insc = Inscripcion.objects.get(id=insc_id)
                    send_attendance_confirmation_email(a, insc)
                except Exception as sync_err:
                    logger.error(f"[Fallback Sync] Error enviando confirmación de asistencia directa: {sync_err}")

        transaction.on_commit(_safe_dispatch_confirmacion_asistencia)
        email_success = True

        return certificado, email_success


def sincronizar_certificados_asistencia() -> int:
    """
    Garantiza que toda Inscripcion con asistencia_confirmada=True en la edición activa
    tenga su registro Certificado correspondiente en la cola si el asistente aún no
    posee certificado registrado para la edición activa (o sin edición asignada).
    Además normaliza certificados con edicion=None hacia la edición activa sin duplicarlos.
    Retorna la cantidad de certificados nuevos encolados.
    """
    from django.db.models import Q
    from .models import PersonalEmpresa
    edicion_activa = Edicion.objects.filter(activa=True).first()
    if not edicion_activa:
        return 0

    # 1. Normalizar certificados existentes con edicion=None asignándoles edicion_activa
    # siempre que no exista ya otro certificado con (asistente_id, edicion_activa, tipo_certificado)
    certs_sin_edicion = list(
        Certificado.objects.filter(edicion__isnull=True).values('id', 'asistente_id', 'tipo_certificado')
    )
    if certs_sin_edicion:
        existentes_activa = set(
            Certificado.objects.filter(
                edicion=edicion_activa,
                asistente_id__in=[c['asistente_id'] for c in certs_sin_edicion],
            ).values_list('asistente_id', 'tipo_certificado')
        )
        ids_a_normalizar = []
        for c in certs_sin_edicion:
            key = (c['asistente_id'], c['tipo_certificado'])
            if key not in existentes_activa:
                ids_a_normalizar.append(c['id'])
                existentes_activa.add(key)
        if ids_a_normalizar:
            Certificado.objects.filter(id__in=ids_a_normalizar).update(edicion=edicion_activa)

    # 2. Asegurar que PersonalEmpresa acreditado en la edición activa tenga su Inscripcion confirmada (filtrado en SQL)
    asistentes_ya_confirmados_qs = Inscripcion.objects.filter(
        edicion=edicion_activa,
        asistencia_confirmada=True,
    ).values_list('asistente_id', flat=True)

    personal_acreditado = list(
        PersonalEmpresa.objects.filter(
            acreditado=True,
            asistente__isnull=False,
        )
        .filter(Q(empresa__edicion=edicion_activa) | Q(empresa__edicion__isnull=True))
        .exclude(asistente_id__in=asistentes_ya_confirmados_qs)
        .select_related('asistente', 'empresa')
    )
    for p in personal_acreditado:
        insc, _ = Inscripcion.objects.get_or_create(
            asistente=p.asistente,
            edicion=edicion_activa,
            defaults={'empresa': p.empresa}
        )
        if not insc.asistencia_confirmada:
            insc.asistencia_confirmada = True
            insc.fecha_confirmacion = p.fecha_acreditacion or timezone.now()
            insc.save(update_fields=['asistencia_confirmada', 'fecha_confirmacion'])

    # 3. Filtrar en SQL únicamente las inscripciones confirmadas que aún no tienen certificado
    # (incluyendo tanto edicion=edicion_activa como edicion__isnull=True, enviados o pendientes)
    asistentes_con_cert_qs = Certificado.objects.filter(
        Q(edicion=edicion_activa) | Q(edicion__isnull=True)
    ).values_list('asistente_id', flat=True)

    inscripciones_sin_cert = list(
        Inscripcion.objects.filter(
            edicion=edicion_activa,
            asistencia_confirmada=True,
        )
        .exclude(asistente_id__in=asistentes_con_cert_qs)
        .select_related('asistente')
    )
    if not inscripciones_sin_cert:
        return 0

    asistentes_con_cert = set()
    nuevos = 0
    for insc in inscripciones_sin_cert:
        asistente = insc.asistente
        if not asistente or asistente.id in asistentes_con_cert:
            continue

        tipo_cert = Certificado.TipoCertificado.ASISTENCIA
        if getattr(asistente, 'disertante_vinculado_id', None):
            tipo_cert = Certificado.TipoCertificado.DISERTANTE
        elif getattr(asistente, 'empresa_vinculada_id', None):
            tipo_cert = Certificado.TipoCertificado.EMPRESA

        _, created = Certificado.objects.get_or_create(
            asistente=asistente,
            edicion=edicion_activa,
            tipo_certificado=tipo_cert,
            defaults={'email_enviado': False}
        )
        if created:
            nuevos += 1
        asistentes_con_cert.add(asistente.id)

    return nuevos


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
    def clean_header(col_name: object) -> str:
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


def generar_plantilla_preacreditacion_staff_empresas() -> bytes:
    """
    Genera un archivo Excel (.xlsx) con el formato oficial para la carga de
    preacreditación masiva de personal de empresas y staff con ejemplos claros.
    """
    import io
    import pandas as pd

    data = [
        {
            "DNI": "35123456",
            "Nombre": "Juan",
            "Apellido": "Pérez",
            "Email": "juan.perez@empresa.com",
            "Teléfono": "1134567890",
            "Tipo": "EMPRESA",
            "Empresa": "Global Express Logística",
            "Cargo": "Coordinador de Stand"
        },
        {
            "DNI": "40987654",
            "Nombre": "Lucía",
            "Apellido": "Gómez",
            "Email": "lucia.gomez@unab.edu.ar",
            "Teléfono": "1198765432",
            "Tipo": "STAFF",
            "Empresa": "",
            "Cargo": "Staff Recepción y Acreditación"
        },
        {
            "DNI": "38555666",
            "Nombre": "Carlos",
            "Apellido": "Rodríguez",
            "Email": "carlos.rodriguez@techlogistics.com",
            "Teléfono": "1144445555",
            "Tipo": "EMPRESA",
            "Empresa": "Tech Logistics S.A.",
            "Cargo": "Promotor Técnico"
        }
    ]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Preacreditacion Staff Empresas', index=False)
        worksheet = writer.sheets['Preacreditacion Staff Empresas']
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 4, 15)
    output.seek(0)
    return output.getvalue()


def procesar_preacreditacion_masiva_staff_empresas(
    file_obj,
    marcar_asistencia: bool = True,
    enviar_email: bool = False,
    edicion_id: int | None = None
) -> Dict[str, Any]:
    """
    Servicio de procesamiento unificado para la preacreditación y confirmación
    de asistencia de personal de Empresas y Staff.

    Lógica de Negocio (Upsert Inteligente):
    - Si la persona ya existe en el sistema (por DNI o Email):
      Actualiza datos de contacto y rol/empresa, asegura inscripción en la edición activa,
      marca asistencia si marcar_asistencia=True, sincroniza PersonalEmpresa y asegura
      el certificado correspondiente en cola.
    - Si la persona NO existe en el sistema:
      Crea el Asistente con sus datos, lo inscribe en la edición activa, marca su asistencia
      de inmediato, sincroniza en PersonalEmpresa y encola su Certificado.
    """
    import re
    import zipfile
    import pandas as pd
    from django.db.models import Q
    from .models import PersonalEmpresa, Acreditacion

    validar_archivo_excel_seguro(file_obj, max_size_mb=10)

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

    def clean_header(col_name: object) -> str:
        c = str(col_name).strip().upper()
        return c.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')

    df.columns = [clean_header(col) for col in df.columns]

    col_dni = next((c for c in df.columns if any(k in c for k in ['DNI', 'DOCUMENTO', 'IDENTIFICACION'])), None)
    col_nombre = next((c for c in df.columns if any(k in c for k in ['NOMBRE', 'FIRST NAME'])), None)
    col_apellido = next((c for c in df.columns if any(k in c for k in ['APELLIDO', 'LAST NAME'])), None)
    col_email = next((c for c in df.columns if any(k in c for k in ['EMAIL', 'CORREO', 'MAIL'])), None)
    col_telefono = next((c for c in df.columns if any(k in c for k in ['TELEFONO', 'CELULAR', 'PHONE'])), None)
    col_tipo = next((c for c in df.columns if any(k in c for k in ['TIPO', 'ROL', 'PERFIL', 'CATEGORIA'])), None)
    col_empresa = next((c for c in df.columns if any(k in c for k in ['EMPRESA', 'SPONSOR', 'STAND', 'ORGANIZACION'])), None)
    col_cargo = next((c for c in df.columns if any(k in c for k in ['CARGO', 'PUESTO', 'FUNCION'])), None)

    if not col_dni and not (col_nombre or col_apellido):
        raise ValueError(
            "Los encabezados de la planilla no coinciden con las columnas requeridas. "
            "Se requiere al menos DNI, Nombre y Apellido (o Nombre Completo)."
        )

    edicion_activa = None
    if edicion_id:
        edicion_activa = Edicion.objects.filter(id=edicion_id).first()
    if not edicion_activa:
        edicion_activa = Edicion.objects.filter(activa=True).first()
    if not edicion_activa:
        raise ValueError("No hay una edición activa configurada en el sistema. Configure o active una edición antes de procesar.")

    # Precargar empresas existentes de la edición
    empresas_qs = Empresa.objects.filter(Q(edicion=edicion_activa) | Q(edicion__isnull=True))
    empresas_cache = {}
    for emp in empresas_qs:
        empresas_cache[emp.nombre_empresa.strip().lower()] = emp
        if emp.cuit:
            cuit_clean = re.sub(r'\D', '', emp.cuit)
            if cuit_clean:
                empresas_cache[cuit_clean] = emp

    EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

    total_filas = 0
    creados = 0
    actualizados = 0
    asistencias_otorgadas = 0
    asistencias_previas = 0
    certificados_encolados = 0
    empresas_afectadas_ids = set()
    errores = []
    resumen_filas = []

    with transaction.atomic():
        for idx, row in df.iterrows():
            row_num = idx + 2

            dni_raw = sanitize_cell_text(row[col_dni]) if col_dni and pd.notna(row[col_dni]) else ""
            nombre_raw = sanitize_cell_text(row[col_nombre]) if col_nombre and pd.notna(row[col_nombre]) else ""
            apellido_raw = sanitize_cell_text(row[col_apellido]) if col_apellido and pd.notna(row[col_apellido]) else ""
            email_raw = sanitize_cell_text(row[col_email]).lower() if col_email and pd.notna(row[col_email]) else ""
            telefono_raw = sanitize_cell_text(row[col_telefono]) if col_telefono and pd.notna(row[col_telefono]) else ""
            tipo_raw = sanitize_cell_text(row[col_tipo]).upper() if col_tipo and pd.notna(row[col_tipo]) else ""
            empresa_raw = sanitize_cell_text(row[col_empresa]) if col_empresa and pd.notna(row[col_empresa]) else ""
            cargo_raw = sanitize_cell_text(row[col_cargo]) if col_cargo and pd.notna(row[col_cargo]) else ""

            # Fila vacía
            if not dni_raw and not nombre_raw and not apellido_raw and not email_raw:
                continue

            total_filas += 1

            # Separar nombre completo si viene junto
            if not apellido_raw and nombre_raw and ' ' in nombre_raw:
                parts = nombre_raw.split(' ', 1)
                nombre_raw = parts[0]
                apellido_raw = parts[1]

            dni_limpio = re.sub(r'\D', '', dni_raw)
            if len(dni_limpio) == 9 and dni_limpio.endswith('0'):
                dni_limpio = dni_limpio[:8]

            if not dni_limpio:
                errores.append(f"Fila {row_num}: DNI ausente o inválido ('{dni_raw}').")
                continue

            if not nombre_raw:
                nombre_raw = f"Participante {dni_limpio}"

            nombre_tit = nombre_raw.title()
            apellido_tit = apellido_raw.title() if apellido_raw else ""

            # Validar o sanitizar email
            email_final = email_raw
            if not email_final or not EMAIL_REGEX.match(email_final):
                email_final = f"sin-email-{dni_limpio}@sin-email.congreso.unab"

            # Determinar rol / tipo
            tipo_upper = tipo_raw.upper()
            es_staff = any(k in tipo_upper for k in ['STAFF', 'ORGANIZ', 'SOPORTE', 'LOGISTICA']) or any(k in cargo_raw.upper() for k in ['STAFF', 'ORGANIZADOR', 'COORDINADOR GENERAL'])
            es_empresa = (not es_staff and (bool(empresa_raw) or any(k in tipo_upper for k in ['EMPRESA', 'STAND', 'SPONSOR', 'EXPOSITOR'])))

            # Resolver empresa si aplica
            empresa_obj = None
            if es_empresa and empresa_raw:
                emp_key = empresa_raw.strip().lower()
                cuit_cand = re.sub(r'\D', '', empresa_raw)
                empresa_obj = empresas_cache.get(emp_key) or (empresas_cache.get(cuit_cand) if cuit_cand else None)
                if not empresa_obj:
                    empresa_obj = Empresa.objects.filter(
                        Q(edicion=edicion_activa) | Q(edicion__isnull=True),
                        nombre_empresa__icontains=empresa_raw.strip()
                    ).first()
                if not empresa_obj:
                    empresa_obj = Empresa.objects.create(
                        nombre_empresa=empresa_raw.strip(),
                        edicion=edicion_activa,
                        estado='CONFIRMADA',
                        nombre_contacto=f"{nombre_tit} {apellido_tit}".strip(),
                        email_contacto=email_final if not email_final.startswith('sin-email') else f"contacto@{re.sub(r'[^a-zA-Z0-9]', '', empresa_raw.lower())}.com"
                    )
                    empresas_cache[emp_key] = empresa_obj

            if empresa_obj:
                empresas_afectadas_ids.add(empresa_obj.id)

            # --- UPSERT ASISTENTE ---
            asistente = Asistente.objects.filter(dni=dni_limpio).first()
            if not asistente and email_final and not email_final.startswith('sin-email'):
                asistente = Asistente.objects.filter(email=email_final).first()

            accion_asistente = "actualizado"
            if asistente:
                asistente.first_name = nombre_tit
                if apellido_tit:
                    asistente.last_name = apellido_tit
                if not asistente.dni and dni_limpio:
                    asistente.dni = dni_limpio
                if telefono_raw:
                    asistente.phone = telefono_raw
                if email_final and not email_final.startswith('sin-email') and (not asistente.email or asistente.email.startswith('sin-email')):
                    asistente.email = email_final
                if es_staff:
                    asistente.rol_especifico = 'STAFF'
                if empresa_obj:
                    asistente.empresa_vinculada = empresa_obj
                asistente.terminos_aceptados = True
                asistente.save()
                actualizados += 1
            else:
                asistente = Asistente.objects.create(
                    dni=dni_limpio,
                    first_name=nombre_tit,
                    last_name=apellido_tit,
                    email=email_final,
                    phone=telefono_raw,
                    profile_type=Asistente.ProfileType.VISITOR,
                    rol_especifico='STAFF' if es_staff else None,
                    empresa_vinculada=empresa_obj if es_empresa else None,
                    terminos_aceptados=True
                )
                accion_asistente = "creado"
                creados += 1

            # --- VINCULAR INSCRIPCIÓN ---
            inscripcion, _ = Inscripcion.objects.get_or_create(
                asistente=asistente,
                edicion=edicion_activa,
                defaults={'empresa': empresa_obj if es_empresa else None}
            )
            if empresa_obj and not inscripcion.empresa:
                inscripcion.empresa = empresa_obj
                inscripcion.save(update_fields=['empresa'])

            # --- MARCAR ASISTENCIA ---
            if marcar_asistencia:
                if not inscripcion.asistencia_confirmada:
                    inscripcion.asistencia_confirmada = True
                    inscripcion.fecha_confirmacion = timezone.now()
                    inscripcion.save(update_fields=['asistencia_confirmada', 'fecha_confirmacion'])
                    asistencias_otorgadas += 1
                else:
                    asistencias_previas += 1

                Acreditacion.objects.get_or_create(
                    inscripcion=inscripcion,
                    defaults={
                        'fecha_acreditacion': inscripcion.fecha_confirmacion or timezone.now(),
                        'metodo': 'MANUAL_DNI',
                        'es_reingreso': False,
                        'observaciones': f'Preacreditación masiva: {"Staff" if es_staff else (empresa_obj.nombre_empresa if empresa_obj else "Empresas")}'
                    }
                )

            # --- SINCRONIZAR PERSONAL EMPRESA ---
            if es_empresa and empresa_obj:
                PersonalEmpresa.objects.update_or_create(
                    empresa=empresa_obj,
                    dni=dni_limpio,
                    defaults={
                        'nombre': nombre_tit,
                        'apellido': apellido_tit,
                        'cargo': cargo_raw or 'Personal de Empresa',
                        'email': email_final if not email_final.startswith('sin-email') else '',
                        'telefono': telefono_raw,
                        'acreditado': marcar_asistencia,
                        'fecha_acreditacion': timezone.now() if marcar_asistencia else None,
                        'asistente': asistente,
                    }
                )

            # --- ENCOLAR CERTIFICADO ---
            cert_tipo = Certificado.TipoCertificado.EMPRESA if (es_empresa and empresa_obj) else Certificado.TipoCertificado.ASISTENCIA
            if marcar_asistencia and inscripcion.asistencia_confirmada:
                _, cert_created = Certificado.objects.get_or_create(
                    asistente=asistente,
                    edicion=edicion_activa,
                    tipo_certificado=cert_tipo,
                    defaults={'email_enviado': False}
                )
                if cert_created:
                    certificados_encolados += 1

            # --- ENVÍO DE EMAIL (OPCIONAL) ---
            if marcar_asistencia and enviar_email and not email_final.startswith('sin-email'):
                try:
                    from .email import send_attendance_confirmation_email
                    send_attendance_confirmation_email(asistente, inscripcion)
                except Exception as mail_err:
                    logger.warning(f"[PREACREDITACION EMAIL] No se pudo enviar email a {email_final}: {mail_err}")

            resumen_filas.append({
                'fila': row_num,
                'dni': dni_limpio,
                'nombre': f"{nombre_tit} {apellido_tit}".strip(),
                'email': email_final,
                'tipo': 'STAFF' if es_staff else ('EMPRESA' if empresa_obj else 'GENERAL'),
                'empresa': empresa_obj.nombre_empresa if empresa_obj else '-',
                'cargo': cargo_raw or '-',
                'accion': accion_asistente,
                'asistencia': 'Confirmada' if marcar_asistencia else 'Pendiente',
                'certificado': cert_tipo if marcar_asistencia else '-',
            })

        # Recalcular cantidad de representantes de empresas afectadas
        for emp_id in empresas_afectadas_ids:
            total_rep = PersonalEmpresa.objects.filter(empresa_id=emp_id).count()
            Empresa.objects.filter(id=emp_id).update(cantidad_representantes=total_rep)

    return {
        'total_filas': total_filas,
        'creados': creados,
        'actualizados': actualizados,
        'asistencias_otorgadas': asistencias_otorgadas,
        'asistencias_previas': asistencias_previas,
        'certificados_encolados': certificados_encolados,
        'empresas_afectadas_count': len(empresas_afectadas_ids),
        'resumen_filas': resumen_filas[:100],
        'total_procesados': len(resumen_filas),
        'errores': errores,
    }






