from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch
from api.models import Asistente, Certificado, Edicion
from api.email import send_certificate_email
import json

class CertificateQueueTests(TestCase):
    def setUp(self):
        # Crear edición activa
        self.edicion, _ = Edicion.objects.get_or_create(
            anio=2026,
            defaults={'nombre': "Congreso de Logística 2026", 'activa': True}
        )
        if not self.edicion.activa:
            self.edicion.activa = True
            self.edicion.save()

        # Crear un superusuario administrador para probar la vista de admin protegida
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@unab.edu.ar',
            password='password123'
        )

        # Crear asistentes de prueba
        self.asistentes = []
        for i in range(5):
            asistente = Asistente.objects.create(
                first_name=f"Asistente_{i}",
                last_name="Test",
                dni=f"1111111{i}",
                email=f"asistente{i}@test.com",
                profile_type="VISITOR"
            )
            self.asistentes.append(asistente)

        # Crear certificados de prueba (inicialmente no enviados)
        self.certificados = []
        for asistente in self.asistentes:
            cert = Certificado.objects.create(
                asistente=asistente,
                tipo_certificado="ASISTENCIA"
            )
            self.certificados.append(cert)

        # URL de la API de procesamiento por lote
        self.batch_url = reverse('admin:process-certificate-batch')

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_send_certificate_email_smtp_failure(self, mock_send):
        """
        Valida que una falla en el servidor SMTP durante el envío individual de certificado
        incremente el contador de intentos y mantenga el estado 'email_enviado' como False.
        """
        mock_send.side_effect = Exception("SMTP Connection Timeout / Auth Failed")

        cert = self.certificados[0]
        self.assertEqual(cert.intentos, 0)
        self.assertFalse(cert.email_enviado)

        # Ejecutar el envío
        result = send_certificate_email(cert)

        # Verificar el retorno en caso de error
        # Nota: Si send_certificate_email retorna una tupla (False, error_msg) en caso de excepción,
        # su primer elemento debe ser False.
        if isinstance(result, tuple):
            success = result[0]
        else:
            success = result
            
        self.assertFalse(success)

        # Recargar de la base de datos
        cert.refresh_from_db()
        self.assertEqual(cert.intentos, 1)
        self.assertFalse(cert.email_enviado)
        self.assertIsNone(cert.fecha_envio)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_process_certificate_batch_api_success(self, mock_send):
        """
        Prueba que la API de procesamiento por lotes funcione correctamente bajo sesión
        de administrador y envíe los certificados por lotes exitosamente.
        """
        # Iniciar sesión como administrador
        self.client.login(username='admin_test', password='password123')

        mock_send.return_value = True

        response = self.client.get(self.batch_url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['status'], 'ok')
        # El batch_size en la vista es 5
        self.assertEqual(data['processed'], 5)
        self.assertEqual(data['errors'], 0)
        self.assertEqual(data['remaining'], 0)
        self.assertEqual(len(data['logs']), 5)

        # Verificar que se hayan actualizado en la base de datos
        for cert in self.certificados:
            cert.refresh_from_db()
            self.assertTrue(cert.email_enviado)
            self.assertIsNotNone(cert.fecha_envio)
            self.assertEqual(cert.intentos, 1)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_process_certificate_batch_api_partial_failure(self, mock_send):
        """
        Prueba la tolerancia a fallos SMTP de la API por lotes.
        Si un correo falla, el lote debe continuar procesando los siguientes correos.
        """
        self.client.login(username='admin_test', password='password123')

        # El primer, segundo, cuarto y quinto éxito. El tercero falla.
        mock_send.side_effect = [None, None, Exception("SMTP Temp failure"), None, None]

        response = self.client.get(self.batch_url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['processed'], 4)
        self.assertEqual(data['errors'], 1)
        self.assertEqual(data['remaining'], 1)  # Queda 1 pendiente porque falló

        # El certificado que falló es el tercero (index 2)
        cert_fallido = self.certificados[2]
        cert_fallido.refresh_from_db()
        self.assertFalse(cert_fallido.email_enviado)
        self.assertEqual(cert_fallido.intentos, 1)

        # Los demás certificados deben estar enviados
        for i, cert in enumerate(self.certificados):
            if i != 2:
                cert.refresh_from_db()
                self.assertTrue(cert.email_enviado)

    def test_process_certificate_batch_api_unauthenticated(self):
        """
        Valida que un usuario no autenticado o no administrador sea redirigido
        o bloqueado al intentar acceder al endpoint de lotes.
        """
        # Intentar acceder sin iniciar sesión
        response = self.client.get(self.batch_url)
        # @admin.site.admin_view redirige al login de Django Admin si no está logueado
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)
