from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from api.models import Empresa, Edicion
from .models import OfertaLaboral

class OfertaLaboralModelTest(TestCase):
    def setUp(self):
        # La edición 2026 ya es creada por las migraciones de 'api'
        self.edicion, _ = Edicion.objects.get_or_create(
            anio=2026, 
            defaults={'nombre': "Edición 2026 Test"}
        )
        self.empresa = Empresa.objects.create(
            edicion=self.edicion,
            nombre_empresa="Test Corp",
            estado="APROBADO"
        )
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
        """Una oferta aprobada y no expirada debe ser activa"""
        oferta = OfertaLaboral.objects.create(**self.base_data)
        self.assertTrue(oferta.is_activa())

    def test_is_activa_false_estado(self):
        """Una oferta no aprobada no debe ser activa"""
        self.base_data['estado'] = OfertaLaboral.Estado.PENDIENTE
        oferta = OfertaLaboral.objects.create(**self.base_data)
        self.assertFalse(oferta.is_activa())

    def test_is_activa_false_expirada(self):
        """Una oferta expirada no debe ser activa"""
        self.base_data['fecha_expiracion'] = timezone.now() - timedelta(days=1)
        oferta = OfertaLaboral.objects.create(**self.base_data)
        self.assertFalse(oferta.is_activa())

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

class OfertaLaboralAPITest(APITestCase):
    def setUp(self):
        self.edicion, _ = Edicion.objects.get_or_create(
            anio=2026, 
            defaults={'nombre': "Edición 2026 Test"}
        )
        self.empresa = Empresa.objects.create(
            edicion=self.edicion,
            nombre_empresa="Test API Corp",
            estado="APROBADO"
        )
        self.empresa1 = Empresa.objects.create(
            edicion=self.edicion,
            nombre_empresa="Empresa Logística A",
            cuit="30-12345678-9",
            estado="APROBADO"
        )
        # Oferta APROBADA y NO expirada
        OfertaLaboral.objects.create(
            empresa=self.empresa,
            titulo_puesto='Activa',
            descripcion='Desc',
            requisitos='Req',
            modalidad=OfertaLaboral.Modalidad.REMOTO,
            ubicacion='BA',
            canal_postulacion='test@test.com',
            estado=OfertaLaboral.Estado.APROBADO,
            fecha_expiracion=timezone.now() + timedelta(days=5)
        )
        # Oferta PENDIENTE
        OfertaLaboral.objects.create(
            empresa=self.empresa,
            titulo_puesto='Pendiente',
            descripcion='Desc',
            requisitos='Req',
            modalidad=OfertaLaboral.Modalidad.REMOTO,
            ubicacion='BA',
            canal_postulacion='test@test.com',
            estado=OfertaLaboral.Estado.PENDIENTE,
            fecha_expiracion=timezone.now() + timedelta(days=5)
        )
        # Oferta EXPIRADA
        OfertaLaboral.objects.create(
            empresa=self.empresa,
            titulo_puesto='Expirada',
            descripcion='Desc',
            requisitos='Req',
            modalidad=OfertaLaboral.Modalidad.REMOTO,
            ubicacion='BA',
            canal_postulacion='test@test.com',
            estado=OfertaLaboral.Estado.APROBADO,
            fecha_expiracion=timezone.now() - timedelta(days=1)
        )

    def test_list_active_offers(self):
        url = reverse('oferta-laboral-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo debe haber 1 oferta (la activa)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo_puesto'], 'Activa')

    def test_filter_by_search(self):
        url = reverse('oferta-laboral-list')
        # Búsqueda que coincide
        response = self.client.get(url, {'q': 'Activa'})
        self.assertEqual(len(response.data), 1)
        # Búsqueda que NO coincide
        response = self.client.get(url, {'q': 'Inexistente'})
        self.assertEqual(len(response.data), 0)

    def test_post_oferta_crea_empresa_si_no_existe(self):
        """Verifica que el POST cree una empresa si no hay match por CUIT/Email."""
        url = reverse('oferta-laboral-create')
        data = {
            'nombre_empresa': 'Nueva Empresa S.A.',
            'email_contacto': 'rrhh@nuevaempresa.com',
            'titulo_puesto': 'Desarrollador Python',
            'descripcion': 'Buscamos experto en Django con ganas de aprender.',
            'requisitos': '3 años de experiencia.',
            'modalidad': 'REMOTO',
            'ubicacion': 'Argentina',
            'canal_postulacion': 'Enviar mail a rrhh@nuevaempresa.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que se creó la empresa
        self.assertTrue(Empresa.objects.filter(nombre_empresa='Nueva Empresa S.A.').exists())
        oferta = OfertaLaboral.objects.get(titulo_puesto='Desarrollador Python')
        self.assertEqual(oferta.estado, 'PENDIENTE')
        self.assertEqual(oferta.empresa.nombre_empresa, 'Nueva Empresa S.A.')

    def test_post_oferta_vincula_empresa_existente(self):
        """Verifica que se vincule a una empresa existente por CUIT."""
        url = reverse('oferta-laboral-create')
        data = {
            'nombre_empresa': 'Nombre Diferente',
            'cuit': '30-12345678-9', # Mismo CUIT que self.empresa1
            'email_contacto': 'otro@test.com',
            'titulo_puesto': 'Puesto de prueba',
            'descripcion': 'Descripción larga para superar validación.',
            'requisitos': 'Requisitos mínimos.',
            'modalidad': 'PRESENCIAL',
            'ubicacion': 'Sede Central',
            'canal_postulacion': 'Link a web'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        oferta = OfertaLaboral.objects.get(titulo_puesto='Puesto de prueba')
        self.assertEqual(oferta.empresa, self.empresa1)
        self.assertEqual(oferta.empresa.nombre_empresa, 'Empresa Logística A')

    def test_filter_by_modalidad(self):
        url = reverse('oferta-laboral-list')
        # Modalidad que coincide
        response = self.client.get(url, {'modalidad': 'REMOTO'})
        self.assertEqual(len(response.data), 1)
        # Modalidad que NO coincide (asumiendo que no hay 'PRESENCIAL' activas)
        response = self.client.get(url, {'modalidad': 'PRESENCIAL'})
        self.assertEqual(len(response.data), 0)

    def test_filter_by_empresa(self):
        url = reverse('oferta-laboral-list')
        # Empresa que coincide
        response = self.client.get(url, {'empresa': self.empresa.id})
        self.assertEqual(len(response.data), 1)
        # Empresa distinta
        otra_empresa = Empresa.objects.create(
            edicion=self.edicion,
            nombre_empresa="Otra",
            estado="APROBADO"
        )
        response = self.client.get(url, {'empresa': otra_empresa.id})
        self.assertEqual(len(response.data), 0)
