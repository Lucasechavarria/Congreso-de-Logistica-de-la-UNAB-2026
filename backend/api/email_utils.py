from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def send_attendee_email(attendee, certificate=None):
    subject = 'Acreditación Convención Logística UNaB'
    message = render_to_string('api/email_acreditacion.html', {
        'attendee': attendee,
    })
    email = EmailMessage(
        subject,
        message,
        to=[attendee.email]
    )
    # Adjuntar QR si existe
    if attendee.qr_code:
        email.attach_file(attendee.qr_code.path)
    # Adjuntar certificado si existe
    if certificate and certificate.pdf:
        email.attach_file(certificate.pdf.path)
    email.content_subtype = 'html'
    email.send()
