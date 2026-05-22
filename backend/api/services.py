import logging
from typing import Tuple, Dict, Any
from django.db import transaction
from django.utils import timezone
from .models import Inscripcion, Certificado, Empresa
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

        # Crear u obtener el certificado de asistencia
        certificado, created = Certificado.objects.get_or_create(
            asistente=inscripcion.asistente,
            tipo_certificado=Certificado.TipoCertificado.ASISTENCIA
        )
        
        # Intentar enviar el certificado por email de forma segura
        email_success = False
        try:
            email_success = send_certificate_email(certificado)
        except Exception as e:
            # Capturar y loggear el error para no invalidar la transacción si falla la conexión SMTP
            logger.error(f"[Services] Error en envío de email de certificado para asistente {inscripcion.asistente.email}: {str(e)}")

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
