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
        self.edicion, _ = Edicion.objects.update_or_create(
            anio=2026, 
            defaults={'nombre': "Congreso 2026", 'activa': True}
        )
        
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
        response = self.client.post(self.inscripcion_individual_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_inscripcion_grupal_success(self):
        # Ajustamos group_size a 2 para coincidir con el numero de miembros
        data = {
            "asistente": {
                "first_name": "Lider",
                "last_name": "Grupo",
                "dni": "99887766",
                "email": "lider@grupo.com",
                "phone": "1122334455",
                "profile_type": "GROUP_REPRESENTATIVE",
                "group_name": "Mi Equipo",
                "group_size": 2,
                "miembros_grupo_nuevos": [
                    {"first_name": "M1", "last_name": "A1", "email": "m1@test.com", "dni": "33445566"},
                    {"first_name": "M2", "last_name": "A2", "email": "m2@test.com", "dni": "44556677"}
                ],
                "terminos_aceptados": True
            }
        }
        response = self.client.post(self.inscripcion_grupal_url, data, format='json')
        if response.status_code != 201:
            print(f"DEBUG ERROR Grupal: {response.json()}")
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
        
        # Verificar en CRM
        response = self.client.get(self.verificar_asistente_url("77889900"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_data = response.json()
        self.assertEqual(res_data['asistente']['dni'], "77889900")
        self.assertTrue(res_data['asistente']['asistencia_confirmada'])

    def test_verificar_empresa_crm(self):
        Empresa.objects.create(
            nombre_empresa="Test CRM", email_empresa="crm@test.com",
            nombre_contacto="Contact", email_contacto="crm@test.com",
            celular_contacto="1122334455", edicion=self.edicion
        )
        response = self.client.get(self.verificar_empresa_url("crm@test.com"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['empresa']['nombre_empresa'], "Test CRM")

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
        response = self.client.post(self.postular_disertante_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_verificar_disertante_crm(self):
        PostulacionDisertante.objects.create(
            nombre_apellido="CRM Disertante", dni="99001122", email="crmd@test.com",
            telefono="1122334455", ciudad_provincia="BSAS", profesion_cargo="Prof",
            empresa_institucion="Uni", titulo_charla="CRM Talk", 
            resumen_charla="Resumen...", objetivos_charla="Obj...", acepta_tyc=True,
            edicion=self.edicion
        )
        response = self.client.get(self.verificar_disertante_url("99001122"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['disertante']['nombre_apellido'], "CRM Disertante")

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