from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Asistente, Inscripcion, Edicion
from .serializers import AsistenteSerializer
from unittest.mock import patch

class RegistrationFlexibilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.edicion, _ = Edicion.objects.get_or_create(
            anio=2026, 
            defaults={'nombre': "Congreso 2026", 'activa': True}
        )
        if not self.edicion.activa:
            self.edicion.activa = True
            self.edicion.save()
        
        self.inscripcion_grupal_url = reverse('inscripcion-grupal')
        
        # Crear un asistente pre-existente para probar duplicados
        self.asistente_existente = Asistente.objects.create(
            first_name="Existente",
            last_name="User",
            dni="12341234",
            email="existente@test.com",
            profile_type="VISITOR"
        )

    @patch('api.serializers.send_group_confirmation_emails', return_value={'total_emails': 2, 'total_fallidos': 0})
    @patch('api.serializers.send_individual_confirmation_email', return_value=True)
    def test_partial_group_registration_success(self, mock_indiv, mock_group):
        """
        Verifica que si un integrante del grupo falla (DNI duplicado), 
        el representante y los otros integrantes vÃ¡lidos se registren igual.
        """
        import traceback
        try:
            # Datos de grupo: 1 representante + 2 miembros nuevos (uno duplicado)
            data = {
                "asistente": {
                    "first_name": "Representante",
                    "last_name": "Grupo",
                    "dni": "99999999",
                    "email": "rep@grupo.com",
                    "profile_type": "GROUP_REPRESENTATIVE",
                    "terminos_aceptados": True,
                    "group_name": "",
                    "group_municipality": "",
                    "group_size": 0,
                    "miembros_grupo_nuevos": [
                        {
                            "first_name": "Miembro",
                            "last_name": "Valido",
                            "dni": "11111111",
                            "email": "valido@test.com"
                        },
                        {
                            "first_name": "Miembro",
                            "last_name": "Duplicado",
                            "dni": "12341234",  # Este ya existe en setUp
                            "email": "duplicado@test.com"
                        }
                    ]
                }
            }
            
            response = self.client.post(self.inscripcion_grupal_url, data, format='json')
            
            # Si hay error 500 o 400, mostrar quÃ© pasÃ³
            if response.status_code != 201:
                print(f"DEBUG: Response status: {response.status_code}")
                print(f"DEBUG: Response data: {response.data}")

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(Asistente.objects.filter(dni="99999999").exists())
            self.assertTrue(Asistente.objects.filter(dni="11111111").exists())
            
            m_duplicado = Asistente.objects.get(dni="12341234")
            self.assertEqual(m_duplicado.first_name, "Miembro")
        except Exception:
            traceback.print_exc()
            raise

    def test_basic_data_enforcement(self):
        """Verifica que falte algun dato bÃ¡sico devuelva error."""
        import traceback
        try:
            data_inv = {
                "asistente": {
                    "first_name": "Sin",
                    "last_name": "DNI",
                    "email": "sin_dni@test.com",
                    "profile_type": "VISITOR",
                    "terminos_aceptados": True
                }
            }
            response = self.client.post(self.inscripcion_grupal_url, data_inv, format='json')
            if response.status_code != status.HTTP_400_BAD_REQUEST:
                print(f"DEBUG: Expected 400, got {response.status_code}. Content: {response.content}")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        except Exception:
            traceback.print_exc()
            raise
