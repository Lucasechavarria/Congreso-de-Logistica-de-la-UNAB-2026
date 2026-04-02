import os
from email.mime.image import MIMEImage
from datetime import date
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
import io
from xhtml2pdf import pisa

# Email oficial del congreso (remitente y copia interna)
CONGRESO_EMAIL = "congresologisticaytransporte@unab.edu.ar"
# Logo negro del congreso (para embeber en templates de email)
LOGO_PATH_DEFAULT = os.path.join('public', 'images', 'CONGRESO-LOGISTICA-2.png')

def get_logo_path():
    """Retorna la ruta absoluta al logo del congreso (negro), priorizando la variable de entorno."""
    logo_env = os.getenv('LOGO_CONGRESO_PATH', LOGO_PATH_DEFAULT)
    logo_path = os.path.join(settings.BASE_DIR, '..', logo_env)
    if os.path.exists(logo_path):
        return logo_path
    # Fallback: intentar ruta directa desde BASE_DIR
    fallback = os.path.join(settings.BASE_DIR, logo_env)
    return fallback


def get_tyc_path(pdf_type='asistente'):
    filename = 'Bases_Asistentes_2026.pdf'
    if pdf_type == 'empresa':
        filename = 'Bases_Empresas_2026.pdf'
    elif pdf_type == 'disertante':
        filename = 'Bases_Disertantes_2026.pdf'
        
    return os.path.join(settings.MEDIA_ROOT, 'static', filename)

def attach_tyc(email, pdf_type='asistente'):
    tyc_path = get_tyc_path(pdf_type)
    if os.path.exists(tyc_path):
        try:
            display_name = os.path.basename(tyc_path).replace('_', ' ')
            with open(tyc_path, 'rb') as f:
                email.attach(display_name, f.read(), 'application/pdf')
            return True
        except Exception as e:
            print(f"[ERROR] No se pudo adjuntar TyC ({pdf_type}): {e}")
    return False
def send_empresa_confirmation_email(empresa_instance):
    # Contexto para la plantilla de email
    context = {
        'empresa_nombre': empresa_instance.nombre_empresa,
        'contacto_nombre': empresa_instance.nombre_contacto,
        'contacto_email': empresa_instance.email_contacto,
        'year': 2026,
        'evento_nombre': 'Congreso de Logística UNAB',
        'evento_fecha': '7 de Noviembre de 2026',
        'evento_hora': '09:00',
        'evento_ubicacion': 'Campus UNAB, Blas Parera 132, Burzaco, Buenos Aires',
        'google_calendar_url': "https://www.google.com/calendar/render?action=TEMPLATE&text=Congreso+de+Logística+UNAB&dates=20261107T120000Z/20261107T210000Z&details=Congreso+de+Logística+UNAB+2026&location=Campus+UNAB,+Buenos+Aires"
    }

    # Renderizar la plantilla HTML
    html_content = render_to_string('api/email/confirmacion_empresa.html', context)
    text_content = strip_tags(html_content)

    logo_path = get_logo_path()

    try:
        email = EmailMultiAlternatives(
            subject='Confirmación de Registro Empresarial - Congreso de Logística UNAB',
            body=text_content,
            from_email=f"Congreso de Logística UNAB <{CONGRESO_EMAIL}>",
            to=[empresa_instance.email_contacto],
            bcc=[CONGRESO_EMAIL]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Adjuntar TyC específico para Empresas
        attach_tyc(email, 'empresa')

        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_img = MIMEImage(f.read(), _subtype="png")
                logo_img.add_header('Content-ID', '<logo_congreso>')
                logo_img.add_header('Content-Disposition', 'inline', filename='logo-congreso.png')
                email.attach(logo_img)
        email.send()
        
        # Alerta al administrador sobre la nueva postulación empresarial
        send_admin_postulation_alert(empresa_instance, "Empresa")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error enviando email a empresa {empresa_instance.nombre_empresa}: {e}")
        return False

def send_confirmation_email(inscripcion_instance):
    asistente = inscripcion_instance.asistente
    # Contexto para la plantilla de email
    context = {
        'asistente_nombre': asistente.nombre_completo,
        'asistente_email': asistente.email,
        'tipo_inscripcion': "Individual", # inscripcion_instance.get_tipo_inscripcion_display(),
        'empresa': inscripcion_instance.empresa.nombre_empresa if inscripcion_instance.empresa else None,
        'year': 2026, # Puedes hacerlo dinámico si lo necesitas
        'evento_nombre': 'Congreso de Logística UNAB',
        'evento_fecha': '7 de Noviembre de 2026',
        'evento_hora': '09:00',
        'evento_ubicacion': 'Campus UNAB, Blas Parera 132, Burzaco, Buenos Aires',
        'google_calendar_url': "https://www.google.com/calendar/render?action=TEMPLATE&text=Congreso+de+Logística+UNAB&dates=20261107T120000Z/20261107T210000Z&details=Congreso+de+Logística+UNAB+2026&location=Campus+UNAB,+Buenos+Aires"
    }

    # Renderizar la plantilla HTML
    html_content = render_to_string('api/email/confirmacion.html', context)
    text_content = strip_tags(html_content) # Versión de texto plano

    logo_path = get_logo_path()

    try:
        # Alerta al administrador del congreso solo si NO es un visitante común
        # Según requerimientos: no saturar con avisos de inscripciones generales.
        bcc_list = []
        if asistente.profile_type not in ["VISITOR", asistente.ProfileType.VISITOR]:
            bcc_list.append(CONGRESO_EMAIL)

        # Crear el email con HTML y texto plano
        email = EmailMultiAlternatives(
            subject='Confirmación de Inscripción al Congreso de Logística UNAB',
            body=text_content,
            from_email=f"Congreso de Logística UNAB <{CONGRESO_EMAIL}>",
            to=[asistente.email],
            bcc=bcc_list
        )
        email.attach_alternative(html_content, "text/html")

        # Adjuntar TyC específico para Asistentes
        attach_tyc(email, 'asistente')

        # Adjuntar el logo embebido
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_img = MIMEImage(f.read(), _subtype="png")
                logo_img.add_header('Content-ID', '<logo_congreso>')
                logo_img.add_header('Content-Disposition', 'inline', filename='logo-congreso.png')
                email.attach(logo_img)
            print(f"[INFO] Logo embebido correctamente: {logo_path}")
        else:
            print(f"[ERROR] No se encontró el logo en {logo_path}")

        email.send()
        return True
    except Exception as e:
        print(f"[ERROR] Error enviando email de confirmación a {asistente.email}: {e}")
        return False

def send_individual_confirmation_email(asistente):
    """
    Envía email de confirmación a un asistente individual.
    """
    try:
        # Determinar el tipo de inscripción
        tipo_inscripcion = "Individual"
        if asistente.profile_type == asistente.ProfileType.STUDENT:
            tipo_inscripcion = "Estudiante"
        elif asistente.profile_type == asistente.ProfileType.TEACHER:
            tipo_inscripcion = "Docente"
        elif asistente.profile_type == asistente.ProfileType.PROFESSIONAL:
            tipo_inscripcion = "Profesional"
        elif asistente.profile_type == asistente.ProfileType.VISITOR:
            tipo_inscripcion = "Visitante"
        elif asistente.profile_type == asistente.ProfileType.GRADUADO:
            tipo_inscripcion = "Graduado"
        elif asistente.profile_type == asistente.ProfileType.PRESS:
            tipo_inscripcion = "Prensa/Influencer"
        elif asistente.profile_type == asistente.ProfileType.OTRO:
            tipo_inscripcion = "Otro"
        
        context = {
            'asistente_nombre': asistente.nombre_completo,
            'asistente_email': asistente.email,
            'tipo_inscripcion': tipo_inscripcion,
            'empresa': None,
            'year': 2026,
            'evento_nombre': 'Congreso de Logística UNAB',
            'evento_fecha': '7 de Noviembre de 2026',
            'evento_hora': '09:00',
            'evento_ubicacion': 'Campus UNAB, Blas Parera 132, Burzaco, Buenos Aires',
            'google_calendar_url': "https://www.google.com/calendar/render?action=TEMPLATE&text=Congreso+de+Logística+UNAB&dates=20261107T120000Z/20261107T210000Z&details=Congreso+de+Logística+UNAB+2026&location=Campus+UNAB,+Buenos+Aires"
        }
        
        html_content = render_to_string('api/email/confirmacion.html', context)
        text_content = strip_tags(html_content)
        
        logo_path = get_logo_path()
        
        # Alerta al administrador del congreso solo si NO es un visitante común
        bcc_list = []
        if asistente.profile_type not in ["VISITOR", asistente.ProfileType.VISITOR]:
            bcc_list.append(CONGRESO_EMAIL)

        email = EmailMultiAlternatives(
            subject='Confirmación de Inscripción al Congreso de Logística UNAB',
            body=text_content,
            from_email=f"Congreso de Logística UNAB <{CONGRESO_EMAIL}>",
            to=[asistente.email],
            bcc=bcc_list
        )
        email.attach_alternative(html_content, "text/html")
        
        # Adjuntar TyC específico para Asistentes
        attach_tyc(email, 'asistente')
        
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_img = MIMEImage(f.read(), _subtype="png")
                logo_img.add_header('Content-ID', '<logo_congreso>')
                logo_img.add_header('Content-Disposition', 'inline', filename='logo-congreso.png')
                email.attach(logo_img)
        
        email.send()
        print(f"[INFO] Email de confirmación enviado a: {asistente.email}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error enviando email a {asistente.email}: {e}")
        return False

def send_postulacion_disertante_email(postulacion):
    """
    Envía email de agradecimiento por postulación al disertante.
    """
    try:
        # Sanetizar ejes temáticos si vienen como string JSON (TextField en DB)
        charla_ejes = postulacion.ejes_tematicos
        if isinstance(charla_ejes, str) and (charla_ejes.startswith('[') or charla_ejes.startswith('{')):
            import json
            try:
                data_parsed = json.loads(charla_ejes)
                if isinstance(data_parsed, list):
                    charla_ejes = ", ".join(data_parsed)
                else:
                    charla_ejes = str(data_parsed)
            except:
                pass
        elif isinstance(charla_ejes, list):
            charla_ejes = ", ".join(charla_ejes)

        context = {
            'disertante_nombre': postulacion.nombre_apellido,
            'charla_titulo': postulacion.titulo_charla,
            'charla_ejes': charla_ejes,
            'year': 2026,
            'evento_nombre': 'Congreso de Logística UNAB',
        }
        
        html_content = render_to_string('api/email/confirmacion_disertante.html', context)
        text_content = strip_tags(html_content)
        
        logo_path = get_logo_path()
        
        email = EmailMultiAlternatives(
            subject='Postulación Recibida - Call for Papers Congreso UNAB 2026',
            body=text_content,
            from_email=f"Congreso de Logística UNAB <{CONGRESO_EMAIL}>",
            to=[postulacion.email],
            bcc=[CONGRESO_EMAIL]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Adjuntar TyC específico para Disertantes
        attach_tyc(email, 'disertante')
        
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_img = MIMEImage(f.read(), _subtype="png")
                logo_img.add_header('Content-ID', '<logo_congreso>')
                logo_img.add_header('Content-Disposition', 'inline', filename='logo-congreso.png')
                email.attach(logo_img)
        
        email.send()
        print(f"[INFO] Email de postulación enviado a: {postulacion.email}")
        
        # Alerta al administrador sobre la nueva postulación
        send_admin_postulation_alert(postulacion, "Disertante")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error enviando email de postulación a {postulacion.email}: {e}")
        return False

def send_bulk_confirmation_email(asistente, es_carga_masiva=False, es_recordatorio=False, fecha_evento=None):
    """
    Envía email de confirmación específico para registros cargados masivamente.
    Incluye solicitud de datos faltantes si es necesario.
    
    Args:
        asistente: Objeto Asistente
        es_carga_masiva: Boolean - Si es parte de una carga masiva
        es_recordatorio: Boolean - Si es un email de recordatorio
        fecha_evento: String - Fecha del evento (formato YYYY-MM-DD), default usa fecha configurada
    """
    try:
        # Configurar fecha del evento
        if fecha_evento:
            from datetime import datetime
            try:
                fecha_dt = datetime.strptime(fecha_evento, '%Y-%m-%d')
                fecha_legible = fecha_dt.strftime('%d de %B de %Y')
                # Mantener formato de fecha para URL de Google Calendar
                fecha_calendar = fecha_evento.replace('-', '') + 'T120000Z/' + fecha_evento.replace('-', '') + 'T210000Z'
            except:
                fecha_legible = '7 de noviembre de 2026'
                fecha_calendar = '20261107T120000Z/20261107T210000Z'
        else:
            fecha_legible = '7 de noviembre de 2026'
            fecha_calendar = '20261107T120000Z/20261107T210000Z'
        
        # Verificar si faltan datos importantes
        datos_faltantes = []
        if not asistente.dni:
            datos_faltantes.append("DNI")
        if not asistente.phone:
            datos_faltantes.append("Teléfono")
        
        # Determinar el tipo de inscripción
        tipo_inscripcion = "Individual"
        if asistente.profile_type == asistente.ProfileType.STUDENT:
            tipo_inscripcion = "Estudiante"
        elif asistente.profile_type == asistente.ProfileType.TEACHER:
            tipo_inscripcion = "Docente"
        elif asistente.profile_type == asistente.ProfileType.PROFESSIONAL:
            tipo_inscripcion = "Profesional"
        elif asistente.profile_type == asistente.ProfileType.VISITOR:
            tipo_inscripcion = "Visitante"
        elif asistente.profile_type == asistente.ProfileType.GRADUADO:
            tipo_inscripcion = "Graduado"
        elif asistente.profile_type == asistente.ProfileType.OTRO:
            tipo_inscripcion = "Otro"
        
        context = {
            'asistente_nombre': asistente.nombre_completo,
            'asistente_email': asistente.email,
            'tipo_inscripcion': tipo_inscripcion,
            'rol_especifico': asistente.rol_especifico if asistente.rol_especifico else None,
            'empresa': None,
            'year': 2026,
            'evento_nombre': 'Congreso de Logística UNAB',
            'evento_fecha': fecha_legible,
            'evento_hora': '09:00',
            'evento_ubicacion': 'Campus UNAB, Blas Parera 132, Burzaco, Buenos Aires',
            'google_calendar_url': f"https://www.google.com/calendar/render?action=TEMPLATE&text=Congreso+de+Logística+UNAB&dates={fecha_calendar}&details=Congreso+de+Logística+UNAB+2026&location=Campus+UNAB,+Buenos+Aires",
            'es_carga_masiva': es_carga_masiva,
            'es_recordatorio': es_recordatorio,
            'datos_faltantes': datos_faltantes
        }
        
        # Usar template específico para carga masiva si hay datos faltantes
        template_name = 'api/email/confirmacion_masiva.html' if es_carga_masiva and datos_faltantes else 'api/email/confirmacion.html'
        
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        
        logo_path = get_logo_path()
        
        # Alerta al administrador solo si NO es un visitante común/estudiante/docente estándar
        # NOTA: Las empresas y disertantes tienen sus propias funciones de alerta detalladas.
        bcc_list = []
        # Definimos quiénes NO saturan el mail del admin: visitantes, estudiantes, docentes, graduados, profesionales.
        # Solo queremos bcc para Prensa, Representantes de Grupo (opcional) o roles especiales si se requiere.
        if asistente.profile_type in [asistente.ProfileType.PRESS, asistente.ProfileType.GROUP_REPRESENTATIVE]:
            bcc_list.append(CONGRESO_EMAIL)

        email = EmailMultiAlternatives(
            subject=f'Confirmación de Inscripción al Congreso de Logística UNAB{subject_suffix}',
            body=text_content,
            from_email=f"Congreso de Logística UNAB <{CONGRESO_EMAIL}>",
            to=[asistente.email],
            bcc=bcc_list
        )
        email.attach_alternative(html_content, "text/html")
        
        # Adjuntar TyC específico para Asistentes
        attach_tyc(email, 'asistente')
        
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_img = MIMEImage(f.read(), _subtype="png")
                logo_img.add_header('Content-ID', '<logo_congreso>')
                logo_img.add_header('Content-Disposition', 'inline', filename='logo-congreso.png')
                email.attach(logo_img)
        
        email.send()
        print(f"[INFO] Email de confirmación {'masiva' if es_carga_masiva else 'individual'} enviado a: {asistente.email}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error enviando email a {asistente.email}: {e}")
        return False

def send_group_confirmation_emails(representante):
    """
    Envía emails de confirmación al representante del grupo y a todos sus miembros.
    """
    emails_enviados = []
    emails_fallidos = []
    
    try:
        # Enviar email al representante
        context_representante = {
            'asistente_nombre': representante.nombre_completo,
            'asistente_email': representante.email,
            'tipo_inscripcion': "Representante de Grupo",
            'empresa': None,
            'year': 2026,
            'evento_nombre': 'Congreso de Logística UNAB',
            'evento_fecha': '7 de Noviembre de 2026',
            'evento_hora': '09:00',
            'evento_ubicacion': 'Campus UNAB, Blas Parera 132, Burzaco, Buenos Aires',
            'google_calendar_url': "https://www.google.com/calendar/render?action=TEMPLATE&text=Congreso+de+Logística+UNAB&dates=20261107T120000Z/20261107T210000Z&details=Congreso+de+Logística+UNAB+2026&location=Campus+UNAB,+Buenos+Aires"
        }
        
        html_content = render_to_string('api/email/confirmacion.html', context_representante)
        text_content = strip_tags(html_content)
        
        logo_path = get_logo_path()
        
        # Notificar al admin solo si es un perfil que requiere seguimiento (Prensa o similar)
        # Para representantes de grupo estándar, evitamos saturar si el usuario así lo prefiere.
        # Por seguridad y seguimiento, el representante suele ser importante, pero lo filtramos si es Visitante.
        bcc_list_rep = []
        if representante.profile_type not in [representante.ProfileType.VISITOR, 'VISITOR']:
            bcc_list_rep.append(CONGRESO_EMAIL)

        email_representante = EmailMultiAlternatives(
            subject='Confirmación de Inscripción Grupal - Congreso de Logística UNAB',
            body=text_content,
            from_email=f"Congreso de Logística UNAB <{CONGRESO_EMAIL}>",
            to=[representante.email],
            bcc=bcc_list_rep
        )
        email_representante.attach_alternative(html_content, "text/html")
        
        # Adjuntar TyC específico para Asistentes
        attach_tyc(email_representante, 'asistente')
        
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_img = MIMEImage(f.read(), _subtype="png")
                logo_img.add_header('Content-ID', '<logo_congreso>')
                logo_img.add_header('Content-Disposition', 'inline', filename='logo-congreso.png')
                email_representante.attach(logo_img)
        
        email_representante.send()
        emails_enviados.append(representante.email)
        print(f"[INFO] Email enviado al representante: {representante.email}")
        
    except Exception as e:
        emails_fallidos.append(f"{representante.email}: {str(e)}")
        print(f"[ERROR] Error enviando email al representante {representante.email}: {e}")
    
    # Enviar emails a cada miembro del grupo
    miembros = representante.get_miembros_grupo()
    for miembro in miembros:
        try:
            context_miembro = {
                'asistente_nombre': miembro.nombre_completo,
                'asistente_email': miembro.email,
                'tipo_inscripcion': f"Miembro del grupo '{representante.group_name}'",
                'empresa': None,
                'year': 2026,
                'evento_nombre': 'Congreso de Logística UNAB',
                'evento_fecha': '7 de Noviembre de 2026',
                'evento_hora': '09:00',
                'evento_ubicacion': 'Campus UNAB, Blas Parera 132, Burzaco, Buenos Aires',
                'google_calendar_url': "https://www.google.com/calendar/render?action=TEMPLATE&text=Congreso+de+Logística+UNAB&dates=20261107T120000Z/20261107T210000Z&details=Congreso+de+Logística+UNAB+2026&location=Campus+UNAB,+Buenos+Aires"
            }
            
            html_content = render_to_string('api/email/confirmacion.html', context_miembro)
            text_content = strip_tags(html_content)
            
            # Miembros del grupo: NO enviar BCC al admin para evitar saturación masiva
            email_miembro = EmailMultiAlternatives(
                subject='Confirmación de Inscripción al Congreso de Logística UNAB',
                body=text_content,
                from_email=f"Congreso de Logística UNAB <{CONGRESO_EMAIL}>",
                to=[miembro.email],
                bcc=[] # Sin copia al admin para miembros individuales
            )
            email_miembro.attach_alternative(html_content, "text/html")
            
            # Adjuntar TyC específico para Asistentes
            attach_tyc(email_miembro, 'asistente')
            
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    logo_img = MIMEImage(f.read(), _subtype="png")
                    logo_img.add_header('Content-ID', '<logo_congreso>')
                    logo_img.add_header('Content-Disposition', 'inline', filename='logo-congreso.png')
                    email_miembro.attach(logo_img)
            
            email_miembro.send()
            emails_enviados.append(miembro.email)
            print(f"[INFO] Email enviado al miembro: {miembro.email}")
            
        except Exception as e:
            emails_fallidos.append(f"{miembro.email}: {str(e)}")
            print(f"[ERROR] Error enviando email al miembro {miembro.email}: {e}")
    
    # Resumen del envío
    total_emails = len(emails_enviados)
    total_fallidos = len(emails_fallidos)
    
    print(f"[INFO] Resumen del envío grupal:")
    print(f"[INFO] - Emails enviados exitosamente: {total_emails}")
    print(f"[INFO] - Emails fallidos: {total_fallidos}")
    
    if emails_fallidos:
        print(f"[ERROR] Emails fallidos: {emails_fallidos}")
    
    return {
        'emails_enviados': emails_enviados,
        'emails_fallidos': emails_fallidos,
        'total_emails': total_emails,
        'total_fallidos': total_fallidos
    }

def send_certificate_email(certificado_instance):
    """
    Genera el certificado en memoria, lo envía por email y lo ELIMINA del servidor inmediatamente.
    """
    asistente = certificado_instance.asistente

    try:
        # Generar el PDF en memoria (save=False para que solo devuelva el buffer)
        pdf_buffer = certificado_instance.generar_pdf(save=False)
        pdf_content = pdf_buffer.getvalue()
        
        # Crear el email
        email = EmailMultiAlternatives(
            subject='Certificado de Asistencia al Congreso de Logística UNAB',
            body='Adjuntamos tu certificado de asistencia al Congreso de Logística UNAB.',
            from_email=f"Congreso de Logística UNAB <{CONGRESO_EMAIL}>",
            to=[asistente.email],
            bcc=[CONGRESO_EMAIL]
        )
        email.attach(
            f'Certificado_{asistente.nombre_completo.replace(" ", "_")}.pdf',
            pdf_content,
            'application/pdf'
        )
        # Enviar el email
        email.send(fail_silently=False)
        
        # --- Marcar como enviado ---
        certificado_instance.email_enviado = True
        certificado_instance.fecha_envio = timezone.now()
        certificado_instance.intentos += 1
        certificado_instance.save(update_fields=['email_enviado', 'fecha_envio', 'intentos'])
        
        print(f"Certificado enviado exitosamente a {asistente.email}")
        return True
        
    except Exception as e:
        import traceback
        error_msg = f"Error enviando certificado a {asistente.email}: {str(e)}\n{traceback.format_exc()}"
        print(f"[ERROR] {error_msg}")
        # En el admin, queremos saber qué pasó
        certificado_instance.intentos += 1
        certificado_instance.save(update_fields=['intentos'])
        return False

def send_admin_postulation_alert(instance, tipo):
    """
    Envía una alerta dedicada al administrador con los detalles de la nueva postulación.
    """
    try:
        datos = {}
        admin_url = ""
        
        if tipo == "Empresa":
            datos = {
                "Empresa": instance.nombre_empresa,
                "Contacto": instance.nombre_contacto,
                "Email": instance.email_contacto,
                "Celular": instance.celular_contacto,
                "Rubro": instance.rubro_logistico,
                "Participación": instance.participacion_opciones,
            }
            admin_url = f"{settings.BASE_URL}/admin/api/empresa/{instance.id}/change/"
        else:
            datos = {
                "Disertante": instance.nombre_apellido,
                "DNI": instance.dni,
                "Email": instance.email,
                "Teléfono": instance.telefono,
                "Profesión": instance.profesion_cargo,
                "Institución": instance.empresa_institucion,
                "Título Charla": instance.titulo_charla,
            }
            admin_url = f"{settings.BASE_URL}/admin/api/postulaciondisertante/{instance.id}/change/"

        context = {
            'tipo_postulacion': tipo,
            'datos': datos,
            'admin_url': admin_url
        }
        
        html_content = render_to_string('api/email/admin_notification_postulacion.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=f'NUEVA POSTULACIÓN: {tipo} - {instance.nombre_empresa if tipo == "Empresa" else instance.nombre_apellido}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[CONGRESO_EMAIL]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        print(f"[INFO] Alerta enviada al administrador para: {instance.id}")
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo enviar alerta al admin: {e}")
        return False


def send_broadcast_batch_email(recipient_list, subject, body_html):
    """
    Envía un email masivo en lotes para evitar saturar el servidor SMTP.
    """
    import os
    import time
    from email.mime.image import MIMEImage
    
    logo_path = get_logo_path()
    
    # Preparar el contenido HTML usando la plantilla base
    context = {'body': body_html}
    full_html = render_to_string('api/email/broadcast_base.html', context)
    text_content = strip_tags(body_html)
    
    enviados = 0
    errores = 0
    BATCH_SIZE = 25 # Lotes pequeños para seguridad
    
    for i in range(0, len(recipient_list), BATCH_SIZE):
        batch = recipient_list[i:i + BATCH_SIZE]
        for email_address in batch:
            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=f"Congreso de Logística UNAB <{CONGRESO_EMAIL}>",
                    to=[email_address]
                )
                msg.attach_alternative(full_html, "text/html")
                
                # Adjuntar logo embebido
                if os.path.exists(logo_path):
                    with open(logo_path, 'rb') as f:
                        logo_img = MIMEImage(f.read(), _subtype="png")
                        logo_img.add_header('Content-ID', '<logo_congreso>')
                        logo_img.add_header('Content-Disposition', 'inline', filename='logo-congreso.png')
                        msg.attach(logo_img)
                
                msg.send()
                enviados += 1
            except Exception as e:
                print(f"[ERROR] No se pudo enviar broadcast a {email_address}: {e}")
                errores += 1
        
        # Pequeña pausa entre lotes si hay más por enviar
        if i + BATCH_SIZE < len(recipient_list):
            time.sleep(2)
            
    return enviados, errores