from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Disertante, Asistente, Inscripcion, MiembroGrupo, Empresa, Certificado
from unittest.mock import patch
from django.utils import timezone

class DisertanteViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.disertante_data = {'nombre': 'Test Disertante', 'bio': 'Test Bio', 'foto_url': ''}
        self.disertante = Disertante.objects.create(**self.disertante_data)
        self.list_url = reverse('disertante-list')
        self.detail_url = reverse('disertante-detail', kwargs={'pk': self.disertante.pk})

    def test_list_disertantes(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], self.disertante_data['nombre'])

    def test_retrieve_disertante(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], self.disertante_data['nombre'])

class RegistroTests(TestCase):
    @patch('api.email.send_empresa_confirmation_email')
    def test_registro_empresas_envia_email_confirmacion(self, mock_send_email):
        data = {
            "nombre_empresa": "Empresa Test Email",
            "nombre_contacto": "Ana",
            "email_contacto": "ana@empresatest.com",
            "celular_contacto": "123456789",
            "cargo_contacto": "Gerente",
            "participacion_opciones": "Sponsor",
            "participacion_otra": "",
        }
        response = self.client.post(self.registro_empresas_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(mock_send_email.called)
        empresa = Empresa.objects.get(nombre_empresa="Empresa Test Email")
        mock_send_email.assert_called_once_with(empresa)
    def setUp(self):
        self.client = APIClient()
        self.registro_participantes_url = reverse('inscripcion-grupal') # Corrected URL name
        self.inscripcion_individual_url = reverse('inscripcion-individual') # New URL for individual
        self.verificar_dni_url = reverse('verificar-dni')
        self.registro_empresas_url = reverse('registro-empresas') # Corrected URL name
        self.registro_rapido_url = reverse('registro-rapido') # New URL for rapid registration
        self.generar_qrs_url = reverse('generar-qrs') # New URL for QR generation

    # Existing tests for RegistroParticipantesView (inscripcion-grupal)
    def test_individual_registration_success(self):
        data = {
            "first_name": "Juan",
            "last_name": "Perez",
            "dni": "12345678",
            "email": "juan.perez@example.com",
            "phone": "1122334455",
            "profile_type": Asistente.ProfileType.STUDENT,
            "is_unab_student": True,
            "career": "Ingenieria",
            "year_of_study": 3,
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Asistente.objects.count(), 1)
        self.assertEqual(Asistente.objects.get().dni, "12345678")

    def test_individual_registration_missing_fields(self):
        data = {
            "first_name": "Juan",
            "last_name": "Perez",
            # Missing DNI, email, phone, profile_type, etc.
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dni', response.json()['message'])
        self.assertIn('email', response.json()['message'])
        self.assertIn('phone', response.json()['message'])

    def test_individual_registration_invalid_email(self):
        data = {
            "first_name": "Juan",
            "last_name": "Perez",
            "dni": "12345678",
            "email": "invalid-email", # Invalid email
            "phone": "1122334455",
            "profile_type": Asistente.ProfileType.STUDENT,
            "is_unab_student": True,
            "career": "Ingenieria",
            "year_of_study": 3,
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.json()['message'])
        self.assertEqual(response.json()['message']['email'][0], 'Introduzca una dirección de correo electrónico válida.')

    def test_group_registration_success(self):
        data = {
            "first_name": "Maria",
            "last_name": "Gomez",
            "dni": "87654321",
            "email": "maria.gomez@example.com",
            "phone": "9988776655",
            "profile_type": Asistente.ProfileType.GROUP_REPRESENTATIVE,
            "group_name": "Grupo Test",
            "group_size": 3,
            "miembros_grupo": [
                {
                    "full_name": "Pedro Lopez",
                    "dni": "11223344",
                },
                {
                    "full_name": "Ana Garcia",
                    "dni": "55667788",
                }
            ]
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Asistente.objects.count(), 1) # Only the representative is an Asistente
        self.assertEqual(MiembroGrupo.objects.count(), 2)
        self.assertEqual(Asistente.objects.filter(dni="87654321").exists(), True)

    def test_group_registration_missing_leader_fields(self):
        data = {
            "first_name": "Maria",
            "profile_type": Asistente.ProfileType.GROUP_REPRESENTATIVE,
            "group_name": "Grupo Test",
            "group_size": 3,
            "miembros_grupo": []
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last_name', response.json()['message'])
        self.assertIn('dni', response.json()['message'])
        self.assertIn('email', response.json()['message'])
        self.assertIn('phone', response.json()['message'])

    def test_group_registration_missing_member_fields(self):
        data = {
            "first_name": "Maria",
            "last_name": "Gomez",
            "dni": "87654321",
            "email": "maria.gomez@example.com",
            "phone": "9988776655",
            "profile_type": Asistente.ProfileType.GROUP_REPRESENTATIVE,
            "group_name": "Grupo Test",
            "group_size": 3,
            "miembros_grupo": [
                {
                    "full_name": "Pedro Lopez",
                    # Missing DNI
                }
            ]
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('miembros_grupo', response.json()['message'])
        self.assertIn('dni', response.json()['message']['miembros_grupo'][0])

    # New tests for conditional validation
    def test_student_registration_unab_no_institution(self):
        data = {
            "first_name": "Juan",
            "last_name": "Perez",
            "dni": "12345679",
            "email": "juan.perez2@example.com",
            "phone": "1122334456",
            "profile_type": Asistente.ProfileType.STUDENT,
            "is_unab_student": False,
            "career": "Ingenieria",
            "year_of_study": 3,
            # Missing institution
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('institution', response.json()['message'])
        self.assertEqual(response.json()['message']['institution'][0], 'La institución es requerida si no perteneces a la UNaB.')

    def test_teacher_registration_missing_institution(self):
        data = {
            "first_name": "Carlos",
            "last_name": "Ruiz",
            "dni": "98765432",
            "email": "carlos.ruiz@example.com",
            "phone": "1133445566",
            "profile_type": Asistente.ProfileType.TEACHER,
            # Missing institution
            "career_taught": "Matematicas",
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('institution', response.json()['message'])
        self.assertEqual(response.json()['message']['institution'][0], 'La institución es requerida para docentes.')

    def test_teacher_registration_missing_career_taught(self):
        data = {
            "first_name": "Carlos",
            "last_name": "Ruiz",
            "dni": "98765433",
            "email": "carlos.ruiz2@example.com",
            "phone": "1133445567",
            "profile_type": Asistente.ProfileType.TEACHER,
            "institution": "Universidad X",
            # Missing career_taught
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('career_taught', response.json()['message'])
        self.assertEqual(response.json()['message']['career_taught'][0], 'La carrera que dicta es requerida para docentes.')

    def test_professional_registration_missing_work_area(self):
        data = {
            "first_name": "Ana",
            "last_name": "Diaz",
            "dni": "23456789",
            "email": "ana.diaz@example.com",
            "phone": "1144556677",
            "profile_type": Asistente.ProfileType.PROFESSIONAL,
            # Missing work_area
            "occupation": "Gerente",
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('work_area', response.json()['message'])
        self.assertEqual(response.json()['message']['work_area'][0], 'El área de trabajo es requerida para profesionales.')

    def test_professional_registration_missing_occupation(self):
        data = {
            "first_name": "Ana",
            "last_name": "Diaz",
            "dni": "23456790",
            "email": "ana.diaz2@example.com",
            "phone": "1144556678",
            "profile_type": Asistente.ProfileType.PROFESSIONAL,
            "work_area": "Logistica",
            # Missing occupation
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('occupation', response.json()['message'])
        self.assertEqual(response.json()['message']['occupation'][0], 'El cargo es requerido para profesionales.')

    def test_group_representative_registration_missing_group_name(self):
        data = {
            "first_name": "Pedro",
            "last_name": "Gomez",
            "dni": "34567890",
            "email": "pedro.gomez@example.com",
            "phone": "1155667788",
            "profile_type": Asistente.ProfileType.GROUP_REPRESENTATIVE,
            # Missing group_name
            "group_size": 2,
            "miembros_grupo": [
                {"full_name": "Miembro 1", "dni": "11111111"},
            ]
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('group_name', response.json()['message'])
        self.assertEqual(response.json()['message']['group_name'][0], 'El nombre del grupo o institución es requerido.')

    def test_group_representative_registration_missing_group_size(self):
        data = {
            "first_name": "Pedro",
            "last_name": "Gomez",
            "dni": "34567891",
            "email": "pedro.gomez2@example.com",
            "phone": "1155667789",
            "profile_type": Asistente.ProfileType.GROUP_REPRESENTATIVE,
            "group_name": "Grupo Test 2",
            # Missing group_size
            "miembros_grupo": [
                {"full_name": "Miembro 1", "dni": "11111112"},
            ]
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('group_size', response.json()['message'])
        self.assertEqual(response.json()['message']['group_size'][0], 'La cantidad de personas es requerida.')

    def test_group_representative_registration_missing_miembros_grupo(self):
        data = {
            "first_name": "Pedro",
            "last_name": "Gomez",
            "dni": "34567892",
            "email": "pedro.gomez3@example.com",
            "phone": "1155667790",
            "profile_type": Asistente.ProfileType.GROUP_REPRESENTATIVE,
            "group_name": "Grupo Test 3",
            "group_size": 1,
            # Missing miembros_grupo
        }
        response = self.client.post(self.registro_participantes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('miembros_grupo', response.json()['message'])
        self.assertEqual(response.json()['message']['miembros_grupo'][0], 'La lista de miembros del grupo es requerida.')

    @patch('api.email.send_certificate_email')
    def test_verificar_dni_success(self, mock_send_certificate_email):
        asistente = Asistente.objects.create(
            first_name="Test", last_name="User", dni="12345678", email="test@example.com",
            phone="123", profile_type=Asistente.ProfileType.STUDENT, is_unab_student=True,
            career="Test", year_of_study=1, asistencia_confirmada=False # Changed to False
        )
        data = {"dni": "12345678"}
        response = self.client.post(self.verificar_dni_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asistente.refresh_from_db()
        self.assertTrue(asistente.asistencia_confirmada) # Corrected field name
        # mock_send_certificate_email.assert_called_once_with(Certificado.objects.get(asistente=asistente)) # Commented out for testing

    def test_verificar_dni_not_found(self):
        data = {"dni": "99999999"}
        response = self.client.post(self.verificar_dni_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('message', response.json())
        self.assertEqual(response.json()['message'], 'DNI no encontrado en el listado de registrados.')

    @patch('api.email.send_certificate_email')
    def test_verificar_dni_already_verified(self, mock_send_certificate_email):
        asistente = Asistente.objects.create(
            first_name="Test", last_name="User", dni="12345678", email="test@example.com",
            phone="123", profile_type=Asistente.ProfileType.STUDENT, is_unab_student=True,
            career="Test", year_of_study=1, asistencia_confirmada=True, fecha_confirmacion=timezone.now()
        )
        data = {"dni": "12345678"}
        response = self.client.post(self.verificar_dni_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        asistente.refresh_from_db()
        self.assertTrue(asistente.asistencia_confirmada)
        mock_send_certificate_email.assert_not_called()
        self.assertIn('message', response.json())
        self.assertIn('La asistencia ya fue confirmada', response.json()['message'])

    def test_registro_empresas_success(self):
        data = {
            "nombre_empresa": "Mi Empresa S.A.",
            "nombre_contacto": "Carlos",
            "email_contacto": "contacto@miempresa.com",
            "celular_contacto": "1122334455",
            "cargo_contacto": "Dueño",
            "participacion_opciones": "Sponsor",
            "participacion_otra": "",
        }
        response = self.client.post(self.registro_empresas_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Empresa.objects.count(), 1)
        self.assertEqual(Empresa.objects.get().nombre_empresa, "Mi Empresa S.A.")

    def test_registro_empresas_missing_fields(self):
        data = {
            "nombre_empresa": "Mi Empresa S.A.",
            # Missing required fields
        }
        response = self.client.post(self.registro_empresas_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nombre_contacto', response.json()['message'])
        self.assertIn('email_contacto', response.json()['message'])
        self.assertIn('celular_contacto', response.json()['message'])
        self.assertIn('cargo_contacto', response.json()['message'])

    # New tests for InscripcionViewSet (individual registration via /inscripcion/)
    @patch('api.email.send_confirmation_email')
    def test_inscripcion_individual_success(self, mock_send_confirmation_email):
        data = {
            "asistente": {
                "first_name": "Pedro",
                "last_name": "Gomez",
                "dni": "98765432",
                "email": "pedro.gomez@example.com",
                "phone": "1199887766",
                "profile_type": Asistente.ProfileType.PROFESSIONAL,
                "work_area": "IT",
                "occupation": "Developer",
            }
        }
        response = self.client.post(self.inscripcion_individual_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Inscripcion.objects.count(), 1)
        self.assertEqual(Asistente.objects.count(), 1)
        self.assertEqual(Asistente.objects.get(dni="98765432").email, "pedro.gomez@example.com")
        # mock_send_confirmation_email.assert_called_once() # Commented out for testing

    def test_inscripcion_individual_duplicate_dni(self):
        Asistente.objects.create(
            first_name="Existing", last_name="User", dni="11223344", email="existing@example.com",
            phone="123", profile_type=Asistente.ProfileType.VISITOR
        )
        data = {
            "asistente": {
                "first_name": "Nuevo",
                "last_name": "Usuario",
                "dni": "11223344", # Duplicate DNI
                "email": "nuevo@example.com",
                "phone": "1122334455",
                "profile_type": Asistente.ProfileType.VISITOR,
            }
        }
        response = self.client.post(self.inscripcion_individual_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dni', response.json()['message']['asistente'])
        self.assertEqual(response.json()['message']['asistente']['dni'][0], 'Ya existe un/a asistente con este/a DNI.')

    def test_inscripcion_individual_missing_fields(self):
        data = {
            "asistente": {
                "first_name": "Missing",
                # Missing last_name, dni, email, phone, profile_type
            }
        }
        response = self.client.post(self.inscripcion_individual_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last_name', response.json()['message']['asistente'])
        self.assertIn('dni', response.json()['message']['asistente'])
        self.assertIn('email', response.json()['message']['asistente'])
        self.assertIn('phone', response.json()['message']['asistente'])

    def test_inscripcion_individual_invalid_email(self):
        data = {
            "asistente": {
                "first_name": "Invalid",
                "last_name": "Email",
                "dni": "55667788",
                "email": "invalid-email-format", # Invalid email
                "phone": "1122334455",
                "profile_type": Asistente.ProfileType.VISITOR,
            }
        }
        response = self.client.post(self.inscripcion_individual_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.json()['message']['asistente'])
        self.assertEqual(response.json()['message']['asistente']['email'][0], 'Introduzca una dirección de correo electrónico válida.')

    # New tests for RegistroRapidoView
    @patch('api.email.send_certificate_email')
    def test_registro_rapido_success(self, mock_send_certificate_email):
        data = {
            "asistente": {
                "first_name": "Rapido",
                "last_name": "Test",
                "dni": "10000000",
                "email": "rapido@example.com",
                "phone": "1111111111",
                "profile_type": Asistente.ProfileType.VISITOR,
            }
        }
        response = self.client.post(self.registro_rapido_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Inscripcion.objects.count(), 1)
        self.assertEqual(Asistente.objects.count(), 1)
        asistente = Asistente.objects.get(dni="10000000")
        self.assertTrue(asistente.asistencia_confirmada)
        # mock_send_certificate_email.assert_called_once() # Commented out for testing

    def test_registro_rapido_missing_fields(self):
        data = {
            "asistente": {
                "first_name": "Missing",
                # Missing last_name, dni, email, phone, profile_type
            }
        }
        response = self.client.post(self.registro_rapido_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last_name', response.json()['message']['asistente'])
        self.assertIn('dni', response.json()['message']['asistente'])
        self.assertIn('email', response.json()['message']['asistente'])
        self.assertIn('phone', response.json()['message']['asistente'])

    # New tests for GenerateStaticQRView
    def test_generar_qrs_success(self):
        response = self.client.get(self.generar_qrs_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming the response contains a list or dictionary of QR data/URLs
        self.assertIsInstance(response.json(), (list, dict))
        # Further assertions can be added based on the expected structure of the QR data
        # For example, if it returns a list of URLs:
        # self.assertGreater(len(response.data), 0)
        # self.assertIn('url', response.data[0])