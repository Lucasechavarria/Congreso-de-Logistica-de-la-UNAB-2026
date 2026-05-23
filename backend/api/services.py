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


def register_asistente_or_group(validated_data: dict, integrantes_data: list = None) -> Asistente:
    """
    Caso de Uso Principal: Registra a un asistente (o representante de grupo),
    crea su inscripción para la edición activa y sus respectivos integrantes.
    Todo de forma transaccional y atómica.
    """
    from .models import Asistente, Edicion, Inscripcion
    from .tasks import task_enviar_confirmacion_grupal, task_enviar_confirmacion_individual
    
    edicion_activa = Edicion.objects.filter(activa=True).first()
    if not edicion_activa:
        raise ValueError("No hay una edición activa configurada en el sistema.")

    with transaction.atomic():
        # Extraer campos de Detalle
        is_unab_student = validated_data.pop('is_unab_student', False)
        institution = validated_data.pop('institution', None)
        career = validated_data.pop('career', None)
        year_of_study = validated_data.pop('year_of_study', None)
        career_taught = validated_data.pop('career_taught', None)
        work_area = validated_data.pop('work_area', None)
        occupation = validated_data.pop('occupation', None)
        group_name = validated_data.pop('group_name', None)
        group_municipality = validated_data.pop('group_municipality', None)
        group_size = validated_data.pop('group_size', 0)
        
        dni = validated_data.get('dni')
        email = validated_data.get('email')

        asistente = None
        if dni:
            asistente = Asistente.objects.filter(dni=dni).first()
        if not asistente and email:
            asistente = Asistente.objects.filter(email=email).first()

        if asistente:
            for attr, value in validated_data.items():
                setattr(asistente, attr, value)
            asistente.save()
        else:
            asistente = Asistente.objects.create(**validated_data)

        # Detalles del representante/asistente
        _upsert_detalles(asistente, {
            'is_unab_student': is_unab_student,
            'institution': institution,
            'career': career,
            'year_of_study': year_of_study,
            'career_taught': career_taught,
            'work_area': work_area,
            'occupation': occupation,
            'group_name': group_name,
            'group_municipality': group_municipality,
            'group_size': group_size
        })

        # Para que el serializer pueda mostrar los valores, los asignamos dinámicamente al objeto en memoria
        asistente.is_unab_student = is_unab_student
        asistente.institution = institution
        asistente.career = career
        asistente.year_of_study = year_of_study
        asistente.career_taught = career_taught
        asistente.work_area = work_area
        asistente.occupation = occupation
        asistente.group_name = group_name
        asistente.group_municipality = group_municipality
        asistente.group_size = group_size

        # Si es un grupo
        if asistente.profile_type == Asistente.ProfileType.GROUP_REPRESENTATIVE:
            if integrantes_data:
                _register_integrantes(asistente, integrantes_data, edicion_activa)
            
            # Encolar email grupal asíncronamente post-commit
            transaction.on_commit(lambda: task_enviar_confirmacion_grupal.delay(asistente.id))
        else:
            # Encolar email individual asíncronamente post-commit
            transaction.on_commit(lambda: task_enviar_confirmacion_individual.delay(asistente.id))

    return asistente
