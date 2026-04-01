
class RecurrenciaTests(BaseCongressTest):
    def test_recurrencia_asistente(self):
        """Un asistente de una edición anterior puede inscribirse en la nueva."""
        edicion_2025 = Edicion.objects.create(anio=2025, nombre="2025", activa=False)
        asistente = Asistente.objects.create(
            first_name="Recurrente", last_name="User", dni="11221122",
            email="recurrente@test.com", profile_type="VISITOR"
        )
        # Inscripción vieja
        Inscripcion.objects.create(asistente=asistente, edicion=edicion_2025, asistencia_confirmada=True)
        
        # Nueva inscripción (2026 activa)
        data = {
            "asistente": {
                "first_name": "Recurrente",
                "last_name": "User",
                "dni": "11221122",
                "email": "recurrente@test.com",
                "profile_type": "VISITOR",
                "terminos_aceptados": True
            }
        }
        # Registrar y omitir envío real de mail
        with patch('api.serializers.send_individual_confirmation_email', return_value=True):
            response = self.client.post(self.inscripcion_individual_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Debe haber 2 inscripciones para 1 único asistente
        self.assertEqual(Inscripcion.objects.filter(asistente=asistente).count(), 2)
        # La nueva inscripción debe tener asistencia pendiente
        nueva_insc = Inscripcion.objects.get(asistente=asistente, edicion=self.edicion)
        self.assertFalse(nueva_insc.asistencia_confirmada)

class CertificateMemoryTests(BaseCongressTest):
    def test_generar_pdf_in_memory(self):
        """Valida que el PDF se genere en memoria sin guardar en disco."""
        asistente = Asistente.objects.create(
            first_name="Cert", last_name="Test", dni="55443322",
            email="cert@test.com", profile_type="VISITOR"
        )
        cert = Certificado.objects.create(asistente=asistente, tipo_certificado="ASISTENCIA")
        
        buffer = cert.generar_pdf(save=False)
        self.assertGreater(len(buffer.getvalue()), 0)
        # El campo pdf_generado debe seguir vacío porque save=False
        self.assertFalse(cert.pdf_generado)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_send_certificate_email_memory(self, mock_send):
        """Valida el envío del email con el adjunto generado on-the-fly."""
        from api.email import send_certificate_email
        asistente = Asistente.objects.create(
            first_name="Mail", last_name="Cert", dni="66554433",
            email="mail@test.com", profile_type="VISITOR"
        )
        cert = Certificado.objects.create(asistente=asistente, tipo_certificado="ASISTENCIA")
        
        success = send_certificate_email(cert)
        self.assertTrue(success)
        self.assertTrue(mock_send.called)
        self.assertTrue(cert.email_enviado)
