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


class MultiCategoryCertificateAdminTests(TestCase):
    def setUp(self):
        self.edicion, _ = Edicion.objects.get_or_create(
            anio=2026,
            defaults={'nombre': "Congreso 2026", 'activa': True}
        )
        self.admin_user = User.objects.create_superuser(
            username='admin_multi',
            email='admin_multi@unab.edu.ar',
            password='password123'
        )
        self.client.login(username='admin_multi', password='password123')

        from api.models import Empresa, Disertante
        self.empresa = Empresa.objects.create(
            nombre_empresa="TechLogistics SA",
            email_empresa="contacto@techlogistics.com",
            rubro_logistico="Automatización y Software"
        )
        self.disertante = Disertante.objects.create(
            nombre="Dra. Valentina Rossi",
            tema_presentacion="Inteligencia Artificial en Cadena de Suministro"
        )
        self.asistente = Asistente.objects.create(
            first_name="Carlos",
            last_name="Gomez",
            email="carlos.gomez@empresa.com",
            dni="30123456",
            profile_type=Asistente.ProfileType.VISITOR,
            terminos_aceptados=True
        )

    def test_asistentes_search_api_multicategory(self):
        """
        Valida que el buscador predictivo devuelva asistentes, disertantes y empresas,
        y respete los filtros por categoría.
        """
        # Búsqueda global "Tech" (debe encontrar Empresa)
        res_emp = self.client.get(reverse('admin:admin-asistentes-search') + '?q=Tech')
        self.assertEqual(res_emp.status_code, 200)
        data_emp = res_emp.json()
        nombres_emp = [item['nombre'] for item in data_emp['results']]
        self.assertIn("TechLogistics SA", nombres_emp)

        # Búsqueda global "Rossi" (debe encontrar Disertante)
        res_dis = self.client.get(reverse('admin:admin-asistentes-search') + '?q=Rossi')
        self.assertEqual(res_dis.status_code, 200)
        data_dis = res_dis.json()
        nombres_dis = [item['nombre'] for item in data_dis['results']]
        self.assertIn("Dra. Valentina Rossi", nombres_dis)

        # Filtro de categoría: Buscar "Tech" en ASISTENTE no debe traer Empresa
        res_filter = self.client.get(reverse('admin:admin-asistentes-search') + '?q=Tech&categoria=ASISTENTE')
        self.assertEqual(res_filter.status_code, 200)
        data_filter = res_filter.json()
        self.assertEqual(len(data_filter['results']), 0)

        # Filtro de categoría EMPRESA
        res_filter_emp = self.client.get(reverse('admin:admin-asistentes-search') + '?q=Tech&categoria=EMPRESA')
        self.assertEqual(res_filter_emp.status_code, 200)
        self.assertEqual(len(res_filter_emp.json()['results']), 1)

    def test_manual_certificate_preview_pdf(self):
        """
        Valida que la vista previa en vivo genere PDFs reales en memoria para
        cada uno de los tres tipos de certificados.
        """
        for tipo in ['ASISTENCIA', 'DISERTANTE', 'EMPRESA']:
            url = f"/admin/manual-certificate/?preview=1&nombre=Prueba%20{tipo}&tipo={tipo}"
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/pdf')
            self.assertTrue(len(response.content) > 1000)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_manual_certificate_post_empresa_y_disertante(self, mock_send):
        """
        Valida la emisión manual de certificados para una Empresa y un Disertante,
        verificando la correcta vinculación en base de datos.
        """
        mock_send.return_value = True

        # Emisión para Empresa seleccionada del predictivo
        post_empresa = {
            'nombre': self.empresa.nombre_empresa,
            'email': self.empresa.email_empresa,
            'tipo': 'EMPRESA',
            'origen_tipo': 'empresa',
            'origen_id': str(self.empresa.id)
        }
        res_emp = self.client.post('/admin/manual-certificate/', post_empresa, follow=True)
        self.assertEqual(res_emp.status_code, 200)

        cert_emp = Certificado.objects.filter(tipo_certificado='EMPRESA', asistente__email=self.empresa.email_empresa).first()
        self.assertIsNotNone(cert_emp)
        self.assertEqual(cert_emp.asistente.empresa_vinculada, self.empresa)

        # Emisión para Disertante seleccionado del predictivo
        post_dis = {
            'nombre': self.disertante.nombre,
            'email': 'valentina.rossi@unab.edu.ar',
            'tipo': 'DISERTANTE',
            'origen_tipo': 'disertante',
            'origen_id': str(self.disertante.id)
        }
        res_dis = self.client.post('/admin/manual-certificate/', post_dis, follow=True)
        self.assertEqual(res_dis.status_code, 200)

        cert_dis = Certificado.objects.filter(tipo_certificado='DISERTANTE', asistente__email='valentina.rossi@unab.edu.ar').first()
        self.assertIsNotNone(cert_dis)
        self.assertEqual(cert_dis.asistente.disertante_vinculado, self.disertante)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_manual_certificate_creation_of_unregistered_entities(self, mock_send):
        """
        Valida que al emitir un certificado para una persona, disertante o empresa
        que NO existe en la base de datos, el sistema cree automáticamente los registros
        correspondientes en sus tablas respectivas aun faltando datos secundarios.
        """
        mock_send.return_value = True
        from api.models import Empresa, Disertante

        # 1. Nueva Persona (Asistente General no registrado previamente, sin DNI ni teléfono)
        res_nuevo_asist = self.client.post('/admin/manual-certificate/', {
            'nombre': 'Esteban Quito',
            'email': 'esteban.quito@externo.org',
            'tipo': 'ASISTENCIA'
        }, follow=True)
        self.assertEqual(res_nuevo_asist.status_code, 200)

        asist_db = Asistente.objects.filter(email='esteban.quito@externo.org').first()
        self.assertIsNotNone(asist_db)
        self.assertEqual(asist_db.first_name, 'Esteban')
        self.assertEqual(asist_db.last_name, 'Quito')
        self.assertIsNone(asist_db.dni)  # Comprueba tolerancia a DNI faltante

        cert_asist = Certificado.objects.filter(asistente=asist_db, tipo_certificado='ASISTENCIA').first()
        self.assertIsNotNone(cert_asist)

        # 2. Nuevo Disertante no registrado previamente
        res_nuevo_dis = self.client.post('/admin/manual-certificate/', {
            'nombre': 'Ing. Roberto Lavalle',
            'email': 'roberto.lavalle@ingenieria.com',
            'tipo': 'DISERTANTE'
        }, follow=True)
        self.assertEqual(res_nuevo_dis.status_code, 200)

        dis_db = Disertante.objects.filter(nombre='Ing. Roberto Lavalle').first()
        self.assertIsNotNone(dis_db)
        self.assertEqual(dis_db.estado, 'APROBADO')
        self.assertEqual(dis_db.edicion, self.edicion)

        asist_dis_db = Asistente.objects.filter(email='roberto.lavalle@ingenieria.com').first()
        self.assertIsNotNone(asist_dis_db)
        self.assertEqual(asist_dis_db.disertante_vinculado, dis_db)

        # 3. Nueva Empresa no registrada previamente
        res_nueva_emp = self.client.post('/admin/manual-certificate/', {
            'nombre': 'Logística Global Express SRL',
            'email': 'facturacion@globalexpress.com.ar',
            'tipo': 'EMPRESA'
        }, follow=True)
        self.assertEqual(res_nueva_emp.status_code, 200)

        emp_db = Empresa.objects.filter(nombre_empresa='Logística Global Express SRL').first()
        self.assertIsNotNone(emp_db)
        self.assertEqual(emp_db.email_empresa, 'facturacion@globalexpress.com.ar')

        asist_emp_db = Asistente.objects.filter(email='facturacion@globalexpress.com.ar').first()
        self.assertIsNotNone(asist_emp_db)
        self.assertEqual(asist_emp_db.empresa_vinculada, emp_db)

    def test_manual_certificate_email_required_for_sending(self):
        """
        Valida que si se elige la acción de enviar por email ('accion': 'enviar'),
        el correo electrónico sea estrictamente OBLIGATORIO y no permita el despacho sin él.
        """
        res = self.client.post('/admin/manual-certificate/', {
            'nombre': 'Persona Sin Email',
            'email': '',
            'tipo': 'ASISTENCIA',
            'accion': 'enviar'
        }, follow=True)
        self.assertEqual(res.status_code, 200)
        messages_list = [m.message for m in res.context['messages']]
        self.assertTrue(any("OBLIGATORIO para enviar el certificado por email" in msg for msg in messages_list))
        # Verifica que no se haya creado ningún certificado
        self.assertFalse(Certificado.objects.filter(asistente__first_name='Persona').exists())

    def test_manual_certificate_direct_download_without_email(self):
        """
        Valida que si se elige 'Generar y Descargar PDF' ('accion': 'descargar'),
        NO sea obligatorio el email: se registre en base de datos y se retorne la descarga directa del PDF.
        """
        res = self.client.post('/admin/manual-certificate/', {
            'nombre': 'Lautaro Entrega Mano',
            'email': '',
            'tipo': 'ASISTENCIA',
            'accion': 'descargar'
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', res['Content-Disposition'])
        self.assertIn('certificado_asistencia_lautaro-entrega-mano.pdf', res['Content-Disposition'])

        # Comprueba que se haya guardado en base de datos
        asist = Asistente.objects.filter(first_name='Lautaro', last_name='Entrega Mano').first()
        self.assertIsNotNone(asist)
        cert = Certificado.objects.filter(asistente=asist).first()
        self.assertIsNotNone(cert)
        self.assertFalse(cert.email_enviado)

    def test_manual_certificate_download_by_cert_id(self):
        """
        Valida que un certificado ya emitido se pueda descargar directamente vía GET ?descargar_cert=<id>
        """
        cert = Certificado.objects.create(
            asistente=self.asistente,
            edicion=self.edicion,
            tipo_certificado='ASISTENCIA'
        )
        res = self.client.get(f'/admin/manual-certificate/?descargar_cert={cert.id}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', res['Content-Disposition'])

    def test_manual_certificate_preview_download_mode(self):
        """
        Valida la descarga directa desde el panel de vista previa vía GET ?preview=1&download=1
        """
        res = self.client.get('/admin/manual-certificate/?preview=1&download=1&nombre=Prueba+Preview&tipo=DISERTANTE')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', res['Content-Disposition'])
        self.assertIn('certificado_disertante_prueba-preview.pdf', res['Content-Disposition'])


