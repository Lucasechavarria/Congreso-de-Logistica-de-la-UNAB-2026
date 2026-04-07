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

    def test_postular_estudiante_exito(self):
        """Verifica persistencia de datos de estudiante."""
        cv_file = SimpleUploadedFile("cv.pdf", b"pdf content", content_type="application/pdf")
        data = {
            'oferta': self.oferta.id,
            'nombre_completo': 'Juan Alumno',
            'email': 'alumno@unab.edu.ar',
            'telefono': '1122334455',
            'es_estudiante': True,
            'institucion': 'Universidad Nacional de Guillermo Brown',
            'cv': cv_file
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        postulacion = PostulacionOferta.objects.get(email='alumno@unab.edu.ar')
        self.assertTrue(postulacion.es_estudiante)
        self.assertEqual(postulacion.institucion, 'Universidad Nacional de Guillermo Brown')

    def test_postular_sin_cv_error(self):
        data = {
            'oferta': self.oferta.id,
            'nombre_completo': 'Test',
            'email': 'test@test.com',
            'telefono': '12345678',
            'es_estudiante': False
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        
        OfertaLaboral.objects.create(
            empresa=self.empresa, titulo_puesto='Activa', descripcion='Desc', modalidad=OfertaLaboral.Modalidad.REMOTO,
            ubicacion='BA', canal_postulacion='test@test.com', estado=OfertaLaboral.Estado.APROBADO,
            fecha_expiracion=timezone.now() + timedelta(days=5)
        )

    def test_list_active_offers(self):
        url = reverse('oferta-laboral-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
