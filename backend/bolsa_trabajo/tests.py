from django.test import TestCase, override_settings
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from api.models import Empresa, Edicion, Asistente, Inscripcion
from .models import OfertaLaboral, PostulacionOferta
from .tasks import enviar_newsletter_semanal

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', CELERY_TASK_ALWAYS_EAGER=True)
class PostulacionAPITest(APITestCase):
    def setUp(self):
        Edicion.objects.all().delete()
        self.edicion = Edicion.objects.create(anio=2030, nombre="Edición 2030 Test", activa=True)
        self.empresa = Empresa.objects.create(edicion=self.edicion, nombre_empresa="Empresa Test", email_contacto="test@empresa.com", estado="APROBADO")
        self.oferta = OfertaLaboral.objects.create(
            empresa=self.empresa,
            titulo_puesto='Puesto Test',
            descripcion='Desc',
            requisitos='Req',
            modalidad=OfertaLaboral.Modalidad.REMOTO,
            ubicacion='BA',
            canal_postulacion='test@test.com',
            estado=OfertaLaboral.Estado.APROBADO,
            fecha_expiracion=timezone.now() + timedelta(days=5)
        )
        self.url = reverse('postulacion-oferta-create')

    def test_postular_exito(self):
        """Verifica que una postulación válida con CV se guarde correctamente."""
        cv_content = b"fake pdf content"
        cv_file = SimpleUploadedFile("cv.pdf", cv_content, content_type="application/pdf")
        
        data = {
            'oferta': self.oferta.id,
            'nombre_completo': 'Candidato Test',
            'email': 'candidato@test.com',
            'telefono': '1122334455',
            'mensaje': 'Hola, quiero el puesto.',
            'cv': cv_file
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PostulacionOferta.objects.filter(email='candidato@test.com').exists())

    def test_postular_sin_cv_error(self):
        """Verifica que no se pueda postular sin adjuntar un CV."""
        data = {
            'oferta': self.oferta.id,
            'nombre_completo': 'Candidato Test',
            'email': 'candidato@test.com',
            'telefono': '1122334455'
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cv', response.data)

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', CELERY_TASK_ALWAYS_EAGER=True)
class OfertaLaboralModelTest(TestCase):
    def setUp(self):
        Edicion.objects.all().delete()
        self.edicion = Edicion.objects.create(anio=2030, nombre="Edición 2030 Test", activa=True)
        self.empresa = Empresa.objects.create(edicion=self.edicion, nombre_empresa="Test Corp", estado="APROBADO")
        self.base_data = {
            'empresa': self.empresa,
            'titulo_puesto': 'Software Engineer',
            'descripcion': 'Test description',
            'requisitos': 'Test requirements',
            'modalidad': OfertaLaboral.Modalidad.REMOTO,
            'ubicacion': 'Buenos Aires',
            'canal_postulacion': 'test@test.com',
            'estado': OfertaLaboral.Estado.APROBADO,
            'fecha_expiracion': timezone.now() + timedelta(days=30)
        }

    def test_is_activa_true(self):
        oferta = OfertaLaboral.objects.create(**self.base_data)
        self.assertTrue(oferta.is_activa())

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', CELERY_TASK_ALWAYS_EAGER=True)
class OfertaLaboralAPITest(APITestCase):
    def setUp(self):
        Edicion.objects.all().delete()
        self.edicion = Edicion.objects.create(anio=2030, nombre="Edición 2030 Test", activa=True)
        self.empresa = Empresa.objects.create(edicion=self.edicion, nombre_empresa="Test API Corp", estado="APROBADO")
        self.empresa1 = Empresa.objects.create(edicion=self.edicion, nombre_empresa="Empresa Logística A", cuit="30-12345678-9", estado="APROBADO")
        
        OfertaLaboral.objects.create(
            empresa=self.empresa, titulo_puesto='Activa', descripcion='Desc', modalidad=OfertaLaboral.Modalidad.REMOTO,
            ubicacion='BA', canal_postulacion='test@test.com', estado=OfertaLaboral.Estado.APROBADO,
            fecha_expiracion=timezone.now() + timedelta(days=5)
        )

    def test_list_active_offers(self):
        url = reverse('oferta-laboral-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo debe haber 1 oferta
        self.assertEqual(len(response.data), 1)

    def test_filter_by_search(self):
        url = reverse('oferta-laboral-list')
        response = self.client.get(url, {'q': 'Activa'})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(url, {'q': 'Inexistente'})
        self.assertEqual(len(response.data), 0)

    def test_post_oferta_crea_empresa_si_no_existe(self):
        url = reverse('oferta-laboral-create')
        data = {
            'nombre_empresa': 'Nueva Empresa S.A.',
            'email_contacto': 'rrhh@nuevaempresa.com',
            'titulo_puesto': 'Desarrollador Python',
            'descripcion': 'Buscamos experto en Django.',
            'requisitos': '3 años de experiencia.',
            'modalidad': 'REMOTO',
            'ubicacion': 'Argentina',
            'canal_postulacion': 'test@test.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Empresa.objects.filter(nombre_empresa='Nueva Empresa S.A.').exists())

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', CELERY_TASK_ALWAYS_EAGER=True)
class NewsletterTest(TestCase):
    def setUp(self):
        Edicion.objects.all().delete()
        self.edicion = Edicion.objects.create(anio=2030, nombre="Edición 2030", activa=True)
        self.asistente = Asistente.objects.create(first_name="Juan", last_name="Perez", dni="12345678", email="juan@test.com", profile_type="VISITOR")
        self.inscripcion_si = Inscripcion.objects.create(asistente=self.asistente, edicion=self.edicion, desea_alertas_laborales=True)
        self.empresa = Empresa.objects.create(nombre_empresa="Test", edicion=self.edicion)
        OfertaLaboral.objects.create(empresa=self.empresa, titulo_puesto="Puesto Reciente", estado="APROBADO", fecha_creacion=timezone.now() - timedelta(days=1), fecha_expiracion=timezone.now() + timedelta(days=1))

    def test_newsletter_filtering(self):
        mail.outbox = []
        enviar_newsletter_semanal()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Puesto Reciente", mail.outbox[0].body)

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', CELERY_TASK_ALWAYS_EAGER=True)
class DesuscripcionAPITest(APITestCase):
    def setUp(self):
        Edicion.objects.all().delete()
        self.edicion = Edicion.objects.create(anio=2030, nombre="Edición 2030", activa=True)
        self.asistente = Asistente.objects.create(first_name="Ana", last_name="Gomez", dni="11223344", email="ana@test.com", profile_type="VISITOR")
        self.inscripcion = Inscripcion.objects.create(asistente=self.asistente, edicion=self.edicion, desea_alertas_laborales=True)

    def test_desuscripcion_exitosa(self):
        url = reverse('desuscribir-alertas')
        response = self.client.get(url, {'email': 'ana@test.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inscripcion.refresh_from_db()
        self.assertFalse(self.inscripcion.desea_alertas_laborales)
