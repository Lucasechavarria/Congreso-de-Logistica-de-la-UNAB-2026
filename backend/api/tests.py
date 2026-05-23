from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import (
    Disertante, Asistente, Inscripcion, MiembroGrupo, 
    Empresa, Certificado, Edicion, PostulacionDisertante,
    InscripcionPrensa
)
from unittest.mock import patch
from django.utils import timezone
import json

class BaseCongressTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.edicion, _ = Edicion.objects.get_or_create(
            anio=2026, 
            defaults={'nombre': "Congreso 2026", 'activa': True}
        )
        if not self.edicion.activa:
            self.edicion.activa = True
            self.edicion.save()
            
        # URLs
        self.registro_url = reverse('registro-unificado')
        self.inscripcion_individual_url = reverse('inscripcion-individual')
        self.inscripcion_grupal_url = reverse('inscripcion-grupal')
        self.registro_empresas_url = reverse('registro-empresas')
        self.registro_rapido_url = reverse('registro-rapido')
        self.postular_disertante_url = reverse('postulaciones-disertantes')
        self.inscripcion_prensa_url = reverse('inscripcion-prensa')
        self.verificar_dni_url = reverse('verificar-dni')
        
    def verificar_asistente_url(self, dni):
        return reverse('verificar-asistente', kwargs={'dni': dni})
        
    def verificar_empresa_url(self, email):
        return reverse('verificar-empresa', kwargs={'email': email})
        
    def verificar_disertante_url(self, dni):
        return reverse('verificar-disertante', kwargs={'dni': dni})
        
class RegistroParticipantesTests(BaseCongressTest):
    def test_registro_estudiante_unab_success(self):
        data = {
            "asistente": {
                "first_name": "Juan",
                "last_name": "Perez",
                "dni": "12345678",
                "email": "juan@unab.com",
                "phone": "1122334455",
                "profile_type": "STUDENT",
                "is_unab_student": True,
                "career": "Ingeniería",
                "year_of_study": 3,
                "terminos_aceptados": True
            }
        }
        with patch('api.serializers.send_individual_confirmation_email', return_value=True):
            response = self.client.post(self.registro_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_inscripcion_individual_success(self):
        data = {
            "asistente": {
                "first_name": "Pedro",
                "last_name": "Gomez",
                "dni": "11223344",
                "email": "pedro@test.com",
                "phone": "2233445566",
                "profile_type": "VISITOR",
                "terminos_aceptados": True
            }
        }
        with patch('api.serializers.send_individual_confirmation_email', return_value=True):
            response = self.client.post(self.inscripcion_individual_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class EmpresaTests(BaseCongressTest):
    def test_registro_empresa_success(self):
        data = {
            "nombre_empresa": "Sponsor S.A.",
            "nombre_contacto": "Carlos",
            "email_contacto": "carlos@sponsor.com",
            "email_empresa": "ventas@sponsor.com",
            "celular_contacto": "1188776655",
            "cargo_contacto": "Gerente",
            "participacion_opciones": "Sponsor Gold",
            "acepta_tyc": True
        }
        response = self.client.post(self.registro_empresas_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class CRMAndVerificationTests(BaseCongressTest):
    def setUp(self):
        super().setUp()
        self.asistente = Asistente.objects.create(
            first_name="Verificado", last_name="User", dni="77889900",
            email="verificado@test.com", phone="1155667788", profile_type="VISITOR"
        )
        Inscripcion.objects.create(asistente=self.asistente, edicion=self.edicion)

    def test_verificar_dni_y_asistencia(self):
        # Confirmar asistencia
        response = self.client.post(self.verificar_dni_url, {"dni": "77889900"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar en CRM (Vía el endpoint de verificación que usa AsistenteSerializer)
        response = self.client.get(self.verificar_asistente_url("77889900"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_data = response.json()
        self.assertEqual(res_data['asistente']['dni'], "77889900")
        self.assertTrue(res_data['asistente']['asistencia_confirmada'])
        
        # Verificar directamente en el modelo Inscripcion
        insc = Inscripcion.objects.get(asistente=self.asistente, edicion=self.edicion)
        self.assertTrue(insc.asistencia_confirmada)

class DisertanteTests(BaseCongressTest):
    def test_postulacion_disertante_success(self):
        data = {
            "nombre_apellido": "Disertante Uno",
            "dni": "55661122",
            "email": "d1@test.com",
            "telefono": "1144332211",
            "ciudad_provincia": "CABA",
            "profesion_cargo": "Speaker",
            "empresa_institucion": "Speaker Co",
            "titulo_charla": "Test Charla",
            "ejes_tematicos": ["Tecnología"], 
            "resumen_charla": "Este es el resumen de la charla que debe ser largo...",
            "objetivos_charla": "Aprender mucho.",
            "publico_dirigido": ["Todos"],
            "modalidad": ["Presencial"],
            "participacion_tipo": ["Invitado"],
            "acepta_tyc": True
        }
        with patch('api.email.send_admin_postulation_alert', return_value=True):
            response = self.client.post(self.postular_disertante_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class PrensaTests(BaseCongressTest):
    def test_inscripcion_prensa_upsert(self):
        data = {
            "nombre_apellido": "Prensa Tres",
            "dni": "88990011",
            "email": "p3@prensa.com",
            "telefono": "1199887766",
            "tipo_perfil": "PERIODISTA",
            "medio_o_canal": "TV Publica",
            "url_perfil_red": "https://tvpublica.com.ar",
            "acepta_tyc": True
        }
        response = self.client.post(self.inscripcion_prensa_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class RecurrenciaTests(BaseCongressTest):
    def test_recurrencia_asistente(self):
        """Un asistente de una edición anterior puede inscribirse en la nueva."""
        edicion_2025, _ = Edicion.objects.get_or_create(anio=2025, defaults={'nombre': "2025", 'activa': False})
        asistente, _ = Asistente.objects.get_or_create(
            dni="11221122",
            defaults={
                'first_name': "Recurrente", 'last_name': "User", 
                'email': "recurrente@test.com", 'profile_type': "VISITOR"
            }
        )
        # Inscripción vieja
        Inscripcion.objects.get_or_create(asistente=asistente, edicion=edicion_2025, defaults={'asistencia_confirmada': True})
        
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
        from .email import send_certificate_email
        asistente = Asistente.objects.create(
            first_name="Mail", last_name="Cert", dni="66554433",
            email="mail@test.com", profile_type="VISITOR"
        )
        cert = Certificado.objects.create(asistente=asistente, tipo_certificado="ASISTENCIA")
        
        success = send_certificate_email(cert)
        self.assertTrue(success)
        self.assertTrue(mock_send.called)
        self.assertTrue(cert.email_enviado)

    def test_asistencia_y_certificado_multi_edicion(self):
        """
        Valida que un asistente con asistencia confirmada en 2025 no interfiera
        con su estado de asistencia en 2026, y pueda obtener certificados separados para cada edición.
        """
        from .services import confirm_asistencia
        
        # 1. Crear edición anterior 2025 e inscripción con asistencia confirmada
        edicion_2025, _ = Edicion.objects.get_or_create(anio=2025, defaults={'nombre': "2025", 'activa': False})
        asistente = Asistente.objects.create(
            first_name="Recurrente", last_name="User", dni="99881122",
            email="recurrente@multi.com", profile_type="VISITOR"
        )
        insc_2025 = Inscripcion.objects.create(asistente=asistente, edicion=edicion_2025, asistencia_confirmada=True)
        cert_2025 = Certificado.objects.create(asistente=asistente, edicion=edicion_2025, tipo_certificado="ASISTENCIA")
        
        # 2. Inscribir para edición activa 2026 (heredada de setUp)
        insc_2026 = Inscripcion.objects.create(asistente=asistente, edicion=self.edicion, asistencia_confirmada=False)
        
        # 3. Comprobar que en 2026 su asistencia es pendiente inicialmente
        self.assertFalse(insc_2026.asistencia_confirmada)
        self.assertTrue(insc_2025.asistencia_confirmada)
        
        # 4. Confirmar asistencia en 2026 y comprobar certificados separados
        cert_2026, success = confirm_asistencia(insc_2026)
        
        # Recargar inscripciones
        insc_2025.refresh_from_db()
        insc_2026.refresh_from_db()
        
        self.assertTrue(insc_2025.asistencia_confirmada)
        self.assertTrue(insc_2026.asistencia_confirmada)
        
        # Deben existir exactamente 2 certificados independientes
        self.assertEqual(Certificado.objects.filter(asistente=asistente, tipo_certificado="ASISTENCIA").count(), 2)
        
        # El certificado de 2025 debe estar intacto
        self.assertEqual(cert_2025.edicion, edicion_2025)
        # El certificado de 2026 debe estar asociado a la edición 2026
        self.assertEqual(cert_2026.edicion, self.edicion)
        self.assertNotEqual(cert_2025.id, cert_2026.id)
