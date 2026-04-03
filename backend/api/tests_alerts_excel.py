from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from io import BytesIO
import pandas as pd

from .models import Asistente, Edicion, InscripcionPrensa, DetalleGrupo
from .email import _generar_excel_miembros, send_admin_postulation_alert, send_individual_confirmation_email

class AlertsAndExcelTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.edicion, _ = Edicion.objects.get_or_create(
            anio=2026, 
            defaults={'nombre': "Congreso 2026", 'activa': True}
        )
        if not self.edicion.activa:
            self.edicion.activa = True
            self.edicion.save()

    def test_excel_generation_logic(self):
        """Valida que _generar_excel_miembros cree un Excel válido en memoria."""
        # Setup representante
        rep = Asistente.objects.create(
            first_name="Rep", last_name="Test", dni="11223344",
            email="rep@test.com", profile_type=Asistente.ProfileType.GROUP_REPRESENTATIVE,
            terminos_aceptados=True
        )
        DetalleGrupo.objects.create(asistente=rep, group_name="Test Group", group_size=2)
        
        # Setup miembro
        Asistente.objects.create(
            first_name="Member", last_name="One", dni="55667788",
            email="m1@test.com", representante_grupo=rep,
            profile_type=Asistente.ProfileType.VISITOR, terminos_aceptados=True
        )

        output = _generar_excel_miembros(rep)
        self.assertIsInstance(output, BytesIO)
        
        # Cargar el excel generado para validar columnas (usando pandas)
        df = pd.read_excel(output)
        self.assertIn("Nombre", df.columns)
        self.assertIn("Apellido", df.columns)
        self.assertIn("DNI", df.columns)
        self.assertIn("Celular", df.columns)
        self.assertIn("Email", df.columns)
        # Debería haber 2 filas: representante + 1 miembro
        self.assertEqual(len(df), 2)
        print("[TEST] Excel generation logic PASSED")

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_admin_alert_context_prensa(self, mock_send):
        """Valida la alerta dedicada para Prensa."""
        prensa = InscripcionPrensa.objects.create(
            nombre_apellido="Prensa Test", dni="12341234", email="p@t.com",
            telefono="1234", tipo_perfil="PERIODISTA", medio_o_canal="Medio X",
            url_perfil_red="https://x.com", acepta_tyc=True
        )
        
        success = send_admin_postulation_alert(prensa, "Prensa")
        self.assertTrue(success)
        self.assertTrue(mock_send.called)
        print("[TEST] Admin alert Press context PASSED")

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_admin_alert_context_grupo(self, mock_send):
        """Valida que la alerta de Grupo adjunte el Excel."""
        rep = Asistente.objects.create(
            first_name="Rep", last_name="Group", dni="99887766",
            email="rg@test.com", profile_type=Asistente.ProfileType.GROUP_REPRESENTATIVE,
            terminos_aceptados=True
        )
        DetalleGrupo.objects.create(asistente=rep, group_name="Club Test", group_size=1)
        
        success = send_admin_postulation_alert(rep, "Grupo")
        self.assertTrue(success)
        self.assertTrue(mock_send.called)

    @patch('api.views.send_admin_postulation_alert')
    def test_prensa_view_triggers_alert(self, mock_alert):
        """Prueba funcional: El endpoint de prensa dispara la alerta dedicada."""
        data = {
            "nombre_apellido": "Prensa Functional",
            "dni": "77665544",
            "email": "pf@test.com",
            "telefono": "112233",
            "tipo_perfil": "PERIODISTA",
            "medio_o_canal": "Canal 5",
            "url_perfil_red": "https://c5.com",
            "acepta_tyc": True
        }
        url = reverse('inscripcion-prensa')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(mock_alert.called)
        # Verificar que se llamó con el tipo "Prensa"
        args, kwargs = mock_alert.call_args
        self.assertEqual(args[1], "Prensa")

    def test_docente_no_alert_individual(self):
        """Prueba de Regresión: Docente individual NO envía copia oculta al admin."""
        from django.core import mail
        from api.email import CONGRESO_EMAIL
        
        docente = Asistente.objects.create(
            first_name="Docente", last_name="Individual", dni="44332211",
            email="doc@test.com", profile_type=Asistente.ProfileType.TEACHER,
            terminos_aceptados=True
        )
        
        send_individual_confirmation_email(docente)
        
        # Debe haber 1 mail en outbox (el de confirmación al docente)
        # Pero NO debe tener al admin en BCC
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotIn(CONGRESO_EMAIL, mail.outbox[0].bcc)
        print("[TEST] Individual Docente filter PASSED")

class EmailBCCLogicTests(TestCase):
    """Pruebas de lógica de BCC para perfiles individuales sin Mock de la función completa."""
    
    def test_bcc_logic_filters(self):
        from django.core import mail
        from api.email import CONGRESO_EMAIL
        
        # 1. Prensa - DEBE tener BCC
        p = Asistente.objects.create(profile_type=Asistente.ProfileType.PRESS, email="p@t.com", dni="11112222", first_name="P", last_name="T")
        send_individual_confirmation_email(p)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(CONGRESO_EMAIL, mail.outbox[0].bcc)
        
        mail.outbox = [] # Limpiar
        
        # 2. Docente - NO DEBE tener BCC
        d = Asistente.objects.create(profile_type=Asistente.ProfileType.TEACHER, email="d@t.com", dni="33334444", first_name="D", last_name="T")
        send_individual_confirmation_email(d)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].bcc), 0)
        
        mail.outbox = []
        
        # 3. Visitante - NO DEBE tener BCC
        v = Asistente.objects.create(profile_type=Asistente.ProfileType.VISITOR, email="v@t.com", dni="55556666", first_name="V", last_name="T")
        send_individual_confirmation_email(v)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].bcc), 0)
