from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch, MagicMock
from api.models import (
    Asistente, Certificado, Edicion, Inscripcion, Acreditacion,
    Empresa, Disertante, PersonalEmpresa, PostulacionDisertante
)
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
        self.batch_url = reverse('admin:process-certificate-batch') + '?forzar=true&delay=0'

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

    @patch('django.utils.timezone.localtime')
    def test_process_certificate_batch_api_blocked_before_18hs(self, mock_localtime):
        """
        Valida que si la hora local es anterior a las 18:00 hs y no se envía forzar=true,
        la API retenga el procesamiento y retorne 'blocked_by_time'.
        """
        self.client.login(username='admin_test', password='password123')
        import datetime
        from zoneinfo import ZoneInfo
        mock_localtime.return_value = datetime.datetime(2026, 11, 6, 11, 30, 0, tzinfo=ZoneInfo('America/Argentina/Buenos_Aires'))

        base_url = reverse('admin:process-certificate-batch')
        response = self.client.get(base_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'blocked_by_time')
        self.assertTrue(data.get('blocked_by_time'))
        self.assertEqual(data.get('processed'), 0)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_confirm_asistencia_flow(self, mock_send):
        """
        Valida que al confirmar asistencia:
        1. asistencia_confirmada se marque como True.
        2. Se cree el certificado con email_enviado=False (retenido en cola para las 18 hs).
        3. Se despache el email de confirmación de asistencia.
        """
        mock_send.return_value = True
        asistente = Asistente.objects.create(
            first_name="Prueba",
            last_name="Asistencia",
            dni="45000111",
            email="asistencia.prueba@unab.edu.ar",
            profile_type="STUDENT"
        )
        from api.models import Inscripcion
        inscripcion = Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion,
            asistencia_confirmada=False
        )

        from api.services import confirm_asistencia
        with self.captureOnCommitCallbacks(execute=True):
            cert, success = confirm_asistencia(inscripcion)

        inscripcion.refresh_from_db()
        self.assertTrue(inscripcion.asistencia_confirmada)
        self.assertIsNotNone(inscripcion.fecha_confirmacion)
        self.assertEqual(cert.tipo_certificado, "ASISTENCIA")
        self.assertFalse(cert.email_enviado)
        self.assertTrue(success)
        self.assertTrue(mock_send.called)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_management_command_procesar_cola(self, mock_send):
        """
        Valida que el comando 'procesar_cola_certificados' procese la cola correctamente con --forzar.
        """
        mock_send.return_value = True
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        call_command('procesar_cola_certificados', batch_size=2, forzar=True, delay=0, pausa_lote=0, stdout=out)
        output = out.getvalue()
        self.assertIn('[FINALIZADO]', output)
        self.assertEqual(Certificado.objects.filter(email_enviado=False).count(), 0)


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

    def test_certificate_email_no_bcc_to_congreso_and_logs_in_admin(self):
        """
        Valida que el envío del certificado de asistencia se envíe ÚNICAMENTE al email
        registrado del asistente, SIN copia oculta (BCC) a congresologisticaytransporte@unab.edu.ar,
        y que deje registro en LogEnvioEmail.
        """
        from django.core import mail
        from api.email import CONGRESO_EMAIL
        from api.models import LogEnvioEmail

        mail.outbox = []
        cert = Certificado.objects.create(
            asistente=self.asistente,
            edicion=self.edicion,
            tipo_certificado='ASISTENCIA'
        )
        result = send_certificate_email(cert)
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        sent_msg = mail.outbox[0]
        self.assertEqual(sent_msg.to, [self.asistente.email])
        self.assertNotIn(CONGRESO_EMAIL, sent_msg.bcc)
        self.assertEqual(sent_msg.bcc, [])

        log_entry = LogEnvioEmail.objects.filter(destinatario=self.asistente.email, tipo_email='certificado_asistencia').first()
        self.assertIsNotNone(log_entry)
        self.assertTrue(log_entry.exitoso)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_certificate_email_blocks_typo_domains_and_logs_error_in_admin(self, mock_send):
        """
        Valida que un email mal escrito (ej. @gmial.com) no se dispare por SMTP (evitando rebotes en la casilla del evento)
        y quede registrado como fallo en LogEnvioEmail para su corrección desde el Admin.
        """
        from api.models import LogEnvioEmail

        asist_typo = Asistente.objects.create(
            first_name="Pedro",
            last_name="Typo",
            email="pedro.typo@gmial.com",
            dni="40999888",
            profile_type=Asistente.ProfileType.VISITOR,
            terminos_aceptados=True
        )
        cert = Certificado.objects.create(
            asistente=asist_typo,
            edicion=self.edicion,
            tipo_certificado='ASISTENCIA'
        )

        result = send_certificate_email(cert)
        self.assertIsInstance(result, tuple)
        self.assertFalse(result[0])
        self.assertIn("gmail.com", result[1])
        self.assertFalse(mock_send.called)

        cert.refresh_from_db()
        self.assertFalse(cert.email_enviado)
        self.assertEqual(cert.intentos, 1)

        log_err = LogEnvioEmail.objects.filter(destinatario="pedro.typo@gmial.com", exitoso=False).first()
        self.assertIsNotNone(log_err)
        self.assertIn("error de tipeo", log_err.error)

    def test_admin_corregir_asistencia_email_view_fixes_data_and_resends(self):
        """
        Valida que desde /admin/corregir-asistencia-email/ el administrador pueda corregir el email,
        nombre y DNI de un participante cuyo envío había fallado, confirmar su asistencia y reenviar el certificado.
        """
        from django.core import mail
        from api.models import Inscripcion, LogEnvioEmail
        from api.email import CONGRESO_EMAIL

        mail.outbox = []
        asist_err = Asistente.objects.create(
            first_name="Lucia",
            last_name="MalEscrito",
            email="lucia@gmial.com",
            dni="38777666",
            profile_type=Asistente.ProfileType.VISITOR,
            terminos_aceptados=True
        )
        cert_err = Certificado.objects.create(
            asistente=asist_err,
            edicion=self.edicion,
            tipo_certificado='ASISTENCIA',
            email_enviado=False,
            intentos=1
        )

        # Enviar corrección desde la vista de admin
        res = self.client.post('/admin/corregir-asistencia-email/', {
            'asistente_id': str(asist_err.id),
            'cert_id': str(cert_err.id),
            'first_name': 'Lucía María',
            'last_name': 'Gómez',
            'dni': '38777665',
            'email': 'lucia.gomez@gmail.com',
            'phone': '1144556677',
            'tipo_certificado': 'ASISTENCIA',
            'confirmar_asistencia': '1',
            'accion': 'guardar_y_enviar',
        }, follow=True)
        self.assertEqual(res.status_code, 200)

        asist_err.refresh_from_db()
        cert_err.refresh_from_db()
        self.assertEqual(asist_err.first_name, 'Lucía María')
        self.assertEqual(asist_err.last_name, 'Gómez')
        self.assertEqual(asist_err.dni, '38777665')
        self.assertEqual(asist_err.email, 'lucia.gomez@gmail.com')
        self.assertTrue(cert_err.email_enviado)

        insc = Inscripcion.objects.filter(asistente=asist_err, edicion=self.edicion).first()
        self.assertIsNotNone(insc)
        self.assertTrue(insc.asistencia_confirmada)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['lucia.gomez@gmail.com'])
        self.assertNotIn(CONGRESO_EMAIL, mail.outbox[0].bcc)

        log_ok = LogEnvioEmail.objects.filter(destinatario='lucia.gomez@gmail.com', exitoso=True).first()
        self.assertIsNotNone(log_ok)


class GDriveBackupAndShieldingTests(TestCase):
    def setUp(self):
        self.edicion, _ = Edicion.objects.get_or_create(
            anio=2026,
            defaults={'nombre': "Congreso 2026", 'activa': True}
        )
        self.asistente = Asistente.objects.create(
            first_name="Esteban",
            last_name="Quito",
            email="esteban.quito@externo.org",
            dni="29999888",
            profile_type=Asistente.ProfileType.VISITOR
        )
        self.inscripcion = Inscripcion.objects.create(
            asistente=self.asistente,
            edicion=self.edicion,
            asistencia_confirmada=True
        )

    def test_attendance_email_shielding_no_congreso_email(self):
        """
        Valida que el email institucional de confirmación de asistencia se envíe ÚNICAMENTE
        al asistente, sin enviar copia (To o BCC) a congresologisticaytransporte@unab.edu.ar.
        """
        from django.core import mail
        from api.email import send_attendance_confirmation_email, CONGRESO_EMAIL

        mail.outbox = []
        enviado = send_attendance_confirmation_email(self.asistente, self.inscripcion)
        self.assertTrue(enviado)
        self.assertEqual(len(mail.outbox), 1)
        
        msg = mail.outbox[0]
        self.assertEqual(msg.to, [self.asistente.email])
        self.assertNotIn(CONGRESO_EMAIL, msg.to)
        self.assertNotIn(CONGRESO_EMAIL, getattr(msg, 'bcc', []))
        self.assertEqual(getattr(msg, 'bcc', []), [])

    def test_generar_paquete_backup_creates_valid_zip_with_excel_and_json(self):
        """
        Valida que generar_paquete_backup() genere un archivo .zip fechado que contenga:
        - El libro Excel consolidado (.xlsx) con las tablas
        - El dump de datos portable (.json)
        - El snapshot SQL compatible con PostgreSQL (_postgres.sql)
        """
        import zipfile
        import os
        from api.backup_service import generar_paquete_backup

        zip_path, zip_name, size_bytes = generar_paquete_backup()
        self.assertTrue(os.path.exists(zip_path))
        self.assertTrue(zip_name.startswith('backup_congreso_'))
        self.assertTrue(zip_name.endswith('.zip'))
        self.assertGreater(size_bytes, 0)

        # Verificar contenido interno del ZIP
        with zipfile.ZipFile(zip_path, 'r') as zf:
            nombres = zf.namelist()
            self.assertTrue(any(n.endswith('.xlsx') for n in nombres), f"Falta archivo .xlsx en {nombres}")
            self.assertTrue(any(n.endswith('_data.json') for n in nombres), f"Falta archivo _data.json en {nombres}")
            self.assertTrue(any(n.endswith('_postgres.sql') for n in nombres), f"Falta archivo _postgres.sql en {nombres}")

        # Limpieza
        if os.path.exists(zip_path):
            os.remove(zip_path)

    def test_celery_beat_schedule_only_certificate_queue_no_scheduled_backups(self):
        """
        Valida que settings.CELERY_BEAT_SCHEDULE haya eliminado todos los respaldos programados
        (dejando los respaldos exclusivamente manuales) y conserve únicamente la cola de certificados.
        """
        from django.conf import settings
        sched = settings.CELERY_BEAT_SCHEDULE

        claves_eliminadas = [
            'respaldo-sistema-viernes-2359',
            'respaldo-sistema-sabado-0600',
            'respaldo-sistema-sabado-1000',
            'respaldo-sistema-sabado-1400',
            'respaldo-sistema-sabado-1800',
        ]
        for k in claves_eliminadas:
            self.assertNotIn(k, sched, f"La clave de respaldo programado {k} no debe existir en CELERY_BEAT_SCHEDULE")

        self.assertIn('procesar-cola-certificados-post-18hs', sched)
        self.assertEqual(
            sched['procesar-cola-certificados-post-18hs']['task'],
            'api.tasks.task_procesar_cola_certificados_lote'
        )

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_enviar_backup_por_email_mocked(self, mock_send):
        """
        Valida que enviar_backup_por_email adjunte el zip y envíe el correo a ambas casillas.
        """
        import os
        from django.conf import settings
        from api.backup_service import enviar_backup_por_email

        mock_send.return_value = True
        temp_file = os.path.join(settings.BASE_DIR, 'test_dummy_email.zip')
        with open(temp_file, 'wb') as f:
            f.write(b"PK\x05\x06" + b"\x00" * 18)

        try:
            destinos = ['echavarrialucas1986@gmail.com', 'congresologisticaytransporte@unab.edu.ar']
            logs = enviar_backup_por_email(temp_file, 'test_dummy_email.zip', destinos)
            self.assertEqual(len(logs), 2)
            self.assertEqual(mock_send.call_count, 2)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_ejecutar_respaldo_programado_actualiza_auditoria(self, mock_send):
        """
        Valida que ejecutar_respaldo_programado genere el zip, envíe email y actualice ConfiguracionRespaldo.
        """
        import os
        from api.models import ConfiguracionRespaldo
        from api.backup_service import ejecutar_respaldo_programado

        mock_send.return_value = True
        config = ConfiguracionRespaldo.get_solo()
        config.activo = True
        config.enviar_por_email = True
        config.email_personal = 'echavarrialucas1986@gmail.com'
        config.email_institucional = 'congresologisticaytransporte@unab.edu.ar'
        config.save()

        resultado = ejecutar_respaldo_programado()
        self.assertEqual(resultado.get('status'), 'ok')
        self.assertTrue(resultado.get('ok'))
        self.assertTrue(resultado.get('archivo').endswith('.zip'))

        config.refresh_from_db()
        self.assertIsNotNone(config.ultimo_respaldo_fecha)
        self.assertEqual(config.ultimo_respaldo_archivo, resultado.get('archivo'))
        self.assertIn("✓ Archivo local generado", config.ultimo_respaldo_estado)
        if resultado.get('zip_path') and os.path.exists(resultado['zip_path']):
            os.remove(resultado['zip_path'])

    def test_admin_respaldos_descarga_directa_zip(self):
        """
        Valida que el endpoint de admin /admin/respaldos/?descargar=zip retorne
        el stream del archivo ZIP con los headers HTTP correctos.
        """
        import os
        from django.conf import settings
        from django.contrib.auth.models import User
        from api.models import ConfiguracionRespaldo
        admin_user, _ = User.objects.get_or_create(username='admin_respaldo_test', is_staff=True, is_superuser=True)
        self.client.force_login(admin_user)

        response = self.client.get('/admin/respaldos/?descargar=zip')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertIn('attachment; filename="backup_congreso_', response['Content-Disposition'])
        config = ConfiguracionRespaldo.get_solo()
        if config.ultimo_respaldo_archivo:
            zip_path = os.path.join(settings.BASE_DIR, 'backups', config.ultimo_respaldo_archivo)
            if os.path.exists(zip_path):
                os.remove(zip_path)


class AcreditacionAndVerificarDNITests(TestCase):
    def setUp(self):
        self.edicion, _ = Edicion.objects.get_or_create(
            anio=2026,
            defaults={'nombre': "Congreso de Logística 2026", 'activa': True}
        )
        if not self.edicion.activa:
            self.edicion.activa = True
            self.edicion.save()

    def test_acreditacion_model_creation(self):
        asistente = Asistente.objects.create(
            first_name="Juan",
            last_name="Perez",
            dni="30111222",
            email="juan.perez@test.com",
            profile_type=Asistente.ProfileType.VISITOR
        )
        inscripcion = Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion,
            asistencia_confirmada=True
        )
        acred = Acreditacion.objects.create(
            inscripcion=inscripcion,
            metodo='QR_ESTATICO_MESA',
            es_reingreso=False,
            observaciones='Ingreso por Tótem 1',
            ip_origen='192.168.1.100'
        )
        self.assertEqual(acred.metodo, 'QR_ESTATICO_MESA')
        self.assertEqual(inscripcion.acreditaciones.count(), 1)
        self.assertEqual(inscripcion.acreditaciones.first(), acred)
        self.assertIn("Acreditación #", str(acred))

    def test_verificar_dni_not_found_returns_404(self):
        response = self.client.post('/api/verificar-dni/', {
            'dni': '99999999',
            'check_only': True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.get('status'), 'error')

    def test_verificar_dni_rejected_empresa_returns_403(self):
        empresa_rechazada = Empresa.objects.create(
            nombre_empresa="Empresa Rechazada S.A.",
            edicion=self.edicion,
            estado='RECHAZADA'
        )
        asistente = Asistente.objects.create(
            first_name="Carlos",
            last_name="Rechazado",
            dni="31222333",
            email="carlos@rechazada.com",
            profile_type=Asistente.ProfileType.PROFESSIONAL,
            empresa_vinculada=empresa_rechazada
        )
        Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion,
            empresa=empresa_rechazada
        )
        response = self.client.post('/api/verificar-dni/', {
            'dni': '31222333',
            'check_only': True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data.get('code'), 'REGISTRATION_REJECTED')
        self.assertIn('recepción', response.data.get('message').lower())

    def test_verificar_dni_rejected_disertante_returns_403(self):
        disertante_rechazado = Disertante.objects.create(
            nombre="Disertante No Admitido",
            edicion=self.edicion,
            estado='RECHAZADO'
        )
        asistente = Asistente.objects.create(
            first_name="Roberto",
            last_name="Disertante",
            dni="32333444",
            email="roberto@disertante.com",
            profile_type=Asistente.ProfileType.PROFESSIONAL,
            disertante_vinculado=disertante_rechazado
        )
        Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion
        )
        response = self.client.post('/api/verificar-dni/', {
            'dni': '32333444',
            'check_only': True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data.get('code'), 'REGISTRATION_REJECTED')

    def test_verificar_dni_already_accredited_returns_409(self):
        now = timezone.now()
        asistente = Asistente.objects.create(
            first_name="Lucia",
            last_name="Acreditada",
            dni="33444555",
            email="lucia@acreditada.com",
            profile_type=Asistente.ProfileType.VISITOR
        )
        Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion,
            asistencia_confirmada=True,
            fecha_confirmacion=now
        )
        response = self.client.post('/api/verificar-dni/', {
            'dni': '33444555',
            'check_only': True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data.get('status'), 'already_accredited')
        self.assertEqual(response.data.get('code'), 'ALREADY_ACCREDITED')
        self.assertIn('hora_acreditacion', response.data)
        self.assertIn('fecha_acreditacion', response.data)
        local_now = timezone.localtime(now)
        self.assertEqual(response.data.get('hora_acreditacion'), local_now.strftime("%H:%M hs"))
        self.assertEqual(response.data.get('fecha_acreditacion'), local_now.strftime("%d/%m/%Y"))
        self.assertIn('asistente', response.data)
        self.assertIn('pantalla', response.data)

    def test_verificar_dni_check_only_flags_provisional_data(self):
        asistente = Asistente.objects.create(
            first_name="Provisorio",
            last_name="Test",
            dni="34555666",
            email="asistente@empresa.temp",
            phone="1111111111",
            profile_type=Asistente.ProfileType.VISITOR
        )
        Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion
        )
        response = self.client.post('/api/verificar-dni/', {
            'dni': '34555666',
            'check_only': True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('status'), 'pending_confirmation')
        self.assertTrue(response.data.get('is_provisional_phone'))
        self.assertTrue(response.data.get('is_provisional_email'))

    def test_verificar_dni_confirm_attendance_creates_acreditacion_and_syncs_personal(self):
        empresa = Empresa.objects.create(
            nombre_empresa="Logística Global",
            edicion=self.edicion,
            estado='CONFIRMADA'
        )
        asistente = Asistente.objects.create(
            first_name="Marcos",
            last_name="Empresarial",
            dni="35666777",
            email="marcos.temp@empresa.temp",
            phone="1111111111",
            profile_type=Asistente.ProfileType.PROFESSIONAL,
            empresa_vinculada=empresa
        )
        inscripcion = Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion,
            empresa=empresa
        )
        personal = PersonalEmpresa.objects.create(
            empresa=empresa,
            nombre="Marcos",
            apellido="Empresarial",
            dni="35666777",
            acreditado=False
        )

        response = self.client.post('/api/verificar-dni/', {
            'dni': '35666777',
            'confirmar': True,
            'email': 'marcos.real@gmail.com',
            'phone': '1144556677',
            'metodo': 'QR_ESTATICO_MESA'
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('status'), 'success')

        # Verificar Inscripcion actualizada
        inscripcion.refresh_from_db()
        self.assertTrue(inscripcion.asistencia_confirmada)
        self.assertIsNotNone(inscripcion.fecha_confirmacion)

        # Verificar Asistente actualizado
        asistente.refresh_from_db()
        self.assertEqual(asistente.email, 'marcos.real@gmail.com')
        self.assertEqual(asistente.phone, '1144556677')

        # Verificar registro en Acreditacion
        acreditaciones = Acreditacion.objects.filter(inscripcion=inscripcion)
        self.assertEqual(acreditaciones.count(), 1)
        acred = acreditaciones.first()
        self.assertEqual(acred.metodo, 'QR_ESTATICO_MESA')
        self.assertFalse(acred.es_reingreso)

        # Verificar sincronización con PersonalEmpresa
        personal.refresh_from_db()
        self.assertTrue(personal.acreditado)
        self.assertIsNotNone(personal.fecha_acreditacion)
        self.assertEqual(personal.asistente, asistente)

    def test_registro_rapido_creates_acreditacion_in_situ(self):
        payload = {
            'asistente': {
                'first_name': 'Camila',
                'last_name': 'Express',
                'dni': '36777888',
                'email': 'camila.express@unab.edu.ar',
                'profile_type': 'VISITOR'
            }
        }
        response = self.client.post('/api/registro-rapido/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('status'), 'success')

        asistente = Asistente.objects.get(dni='36777888')
        inscripcion = Inscripcion.objects.get(asistente=asistente, edicion=self.edicion)
        self.assertTrue(inscripcion.asistencia_confirmada)

        acred = Acreditacion.objects.filter(inscripcion=inscripcion).first()
        self.assertIsNotNone(acred)
        self.assertEqual(acred.metodo, 'IN_SITU')

    def test_verificar_dni_provisional_check_does_not_flag_valid_localities(self):
        """Valida que un email real con 'temperley' en el usuario no se marque como provisorio."""
        asistente = Asistente.objects.create(
            first_name="Marcos",
            last_name="Temperley",
            dni="37111222",
            email="marcos.temperley@gmail.com",
            phone="1144332211",
            profile_type=Asistente.ProfileType.VISITOR
        )
        Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion
        )
        response = self.client.post('/api/verificar-dni/', {
            'dni': '37111222',
            'check_only': True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data.get('is_provisional_email'))
        self.assertFalse(response.data.get('is_provisional_phone'))

    def test_verificar_dni_blocks_confirmation_with_provisional_email_or_phone(self):
        """Valida que si se intenta confirmar con datos provisorios, el backend rechace con HTTP 400 PROVISIONAL_DATA_REQUIRED."""
        asistente = Asistente.objects.create(
            first_name="Temporal",
            last_name="Usuario",
            dni="38222333",
            email="temp.user@empresa.temp",
            phone="1111111111",
            profile_type=Asistente.ProfileType.VISITOR
        )
        inscripcion = Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion
        )
        # Intentar confirmar sin corregir datos
        response = self.client.post('/api/verificar-dni/', {
            'dni': '38222333',
            'confirmar': True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('code'), 'PROVISIONAL_DATA_REQUIRED')
        inscripcion.refresh_from_db()
        self.assertFalse(inscripcion.asistencia_confirmada)
        self.assertEqual(Acreditacion.objects.filter(inscripcion=inscripcion).count(), 0)

    def test_verificar_dni_not_enrolled_for_active_edition_returns_404_not_registered(self):
        """Valida que un asistente registrado en otra edición pero no en la activa devuelva 404 NOT_REGISTERED."""
        otra_edicion, _ = Edicion.objects.get_or_create(anio=2025, defaults={'nombre': "Congreso 2025", 'activa': False})
        asistente = Asistente.objects.create(
            first_name="Pasado",
            last_name="Anterior",
            dni="39333444",
            email="pasado@test.com",
            phone="1199887766",
            profile_type=Asistente.ProfileType.VISITOR
        )
        Inscripcion.objects.create(
            asistente=asistente,
            edicion=otra_edicion
        )
        response = self.client.post('/api/verificar-dni/', {
            'dni': '39333444',
            'check_only': True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.get('code'), 'NOT_REGISTERED')

    def test_verificar_dni_concurrency_race_condition(self):
        """
        Valida que si dos solicitudes de confirmación concurrente llegan para la misma inscripción,
        la primera entrega HTTP 200 y la segunda entrega HTTP 409 ALREADY_ACCREDITED,
        generando exactamente un solo registro de Acreditacion.
        """
        asistente = Asistente.objects.create(
            first_name="Concurrente",
            last_name="Test",
            dni="41000111",
            email="concurrente@unab.edu.ar",
            phone="1155443322",
            profile_type=Asistente.ProfileType.VISITOR
        )
        inscripcion = Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion
        )

        res1 = self.client.post('/api/verificar-dni/', {
            'dni': '41000111',
            'confirmar': True
        }, content_type='application/json')
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.data.get('status'), 'success')

        res2 = self.client.post('/api/verificar-dni/', {
            'dni': '41000111',
            'confirmar': True
        }, content_type='application/json')
        self.assertEqual(res2.status_code, 409)
        self.assertEqual(res2.data.get('code'), 'ALREADY_ACCREDITED')

        # Comprobar que solo existe 1 registro de Acreditacion
        self.assertEqual(Acreditacion.objects.filter(inscripcion=inscripcion).count(), 1)

    def test_verificar_dni_ip_extraction_and_sanitization(self):
        """Valida que IP con puerto o proxy múltiple se guarde sanitizada en Acreditacion."""
        asistente = Asistente.objects.create(
            first_name="IP",
            last_name="Proxy",
            dni="42111222",
            email="ip.proxy@test.com",
            phone="1122334455",
            profile_type=Asistente.ProfileType.VISITOR
        )
        inscripcion = Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion
        )
        response = self.client.post(
            '/api/verificar-dni/',
            {'dni': '42111222', 'confirmar': True},
            content_type='application/json',
            HTTP_X_FORWARDED_FOR='190.220.10.5:8080, 10.0.0.1'
        )
        self.assertEqual(response.status_code, 200)
        acred = Acreditacion.objects.filter(inscripcion=inscripcion).first()
        self.assertIsNotNone(acred)
        self.assertEqual(acred.ip_origen, '190.220.10.5')

    def test_verificar_dni_disertante_rejected_in_old_edition_does_not_block_current_edition(self):
        """
        Valida que un disertante con estado RECHAZADO en una edición anterior (no activa)
        pueda acreditarse como asistente general en la edición 2026 activa sin ser bloqueado.
        """
        edicion_ant, _ = Edicion.objects.get_or_create(anio=2024, defaults={'nombre': 'Congreso 2024', 'activa': False})
        dis_ant = Disertante.objects.create(
            nombre="Disertante Pasado",
            estado='RECHAZADO',
            edicion=edicion_ant
        )
        asistente = Asistente.objects.create(
            first_name="Disertante",
            last_name="Pasado",
            dni="43111222",
            email="dis.pasado@unab.edu.ar",
            phone="1144332211",
            profile_type=Asistente.ProfileType.VISITOR,
            disertante_vinculado=dis_ant
        )
        Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion
        )
        response = self.client.post('/api/verificar-dni/', {
            'dni': '43111222',
            'check_only': True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('status'), 'pending_confirmation')

    def test_verificar_dni_empresa_rejected_in_old_edition_does_not_block_current_edition(self):
        """
        Valida que una empresa rechazada en una edición anterior no bloquee
        la acreditación del participante en la edición activa.
        """
        edicion_ant, _ = Edicion.objects.get_or_create(anio=2024, defaults={'nombre': 'Congreso 2024', 'activa': False})
        empresa_ant = Empresa.objects.create(
            nombre_empresa="Empresa Vieja Rechazada",
            estado='RECHAZADA',
            edicion=edicion_ant
        )
        asistente = Asistente.objects.create(
            first_name="Empleado",
            last_name="Viejo",
            dni="44222333",
            email="empleado.viejo@test.com",
            phone="1155443322",
            profile_type=Asistente.ProfileType.PROFESSIONAL,
            empresa_vinculada=empresa_ant
        )
        Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion
        )
        response = self.client.post('/api/verificar-dni/', {
            'dni': '44222333',
            'check_only': True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('status'), 'pending_confirmation')

    def test_verificar_dni_barcode_with_trailing_zero_is_normalized(self):
        """
        Valida que un lector de código de barras que envía 9 dígitos con '0' final
        (ej: 453334440) se normalice a 8 dígitos (45333444) y acredite correctamente.
        """
        asistente = Asistente.objects.create(
            first_name="Codigo",
            last_name="Barras",
            dni="45333444",
            email="barras@test.com",
            phone="1122446688",
            profile_type=Asistente.ProfileType.VISITOR
        )
        inscripcion = Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion
        )
        response = self.client.post('/api/verificar-dni/', {
            'dni': '453334440',
            'confirmar': True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        inscripcion.refresh_from_db()
        self.assertTrue(inscripcion.asistencia_confirmada)

    def test_verificar_dni_syncs_personal_empresa_contact_fields(self):
        """
        Valida que al confirmar asistencia y actualizar datos, PersonalEmpresa
        también reciba el email y teléfono reales actualizados.
        """
        empresa = Empresa.objects.create(
            nombre_empresa="Tech Logistics SA",
            edicion=self.edicion,
            estado='CONFIRMADA'
        )
        asistente = Asistente.objects.create(
            first_name="Ramiro",
            last_name="Preacreditado",
            dni="46444555",
            email="acreditado_46444555@empresa.temp",
            phone="1111111111",
            profile_type=Asistente.ProfileType.PROFESSIONAL,
            empresa_vinculada=empresa
        )
        inscripcion = Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion,
            empresa=empresa
        )
        personal = PersonalEmpresa.objects.create(
            empresa=empresa,
            nombre="Ramiro",
            apellido="Preacreditado",
            dni="46444555",
            email="",
            telefono="",
            acreditado=False
        )

        response = self.client.post('/api/verificar-dni/', {
            'dni': '46444555',
            'confirmar': True,
            'email': 'ramiro.real@gmail.com',
            'phone': '1133221100'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        personal.refresh_from_db()
        self.assertTrue(personal.acreditado)
        self.assertEqual(personal.email, 'ramiro.real@gmail.com')
        self.assertEqual(personal.telefono, '1133221100')

    def test_registro_rapido_sets_es_reingreso_true_if_already_accredited(self):
        """
        Valida que si un asistente ya acreditado vuelve a registrarse por RegistroRapido,
        la nueva auditoría en Acreditacion registre es_reingreso=True.
        """
        asistente = Asistente.objects.create(
            first_name="Reingresante",
            last_name="Rapido",
            dni="47555666",
            email="reingreso.rapido@test.com",
            phone="1199881122",
            profile_type=Asistente.ProfileType.VISITOR
        )
        inscripcion = Inscripcion.objects.create(
            asistente=asistente,
            edicion=self.edicion,
            asistencia_confirmada=True,
            fecha_confirmacion=timezone.now()
        )
        Acreditacion.objects.create(
            inscripcion=inscripcion,
            metodo='QR_ESTATICO_MESA',
            es_reingreso=False
        )

        payload = {
            'asistente': {
                'first_name': 'Reingresante',
                'last_name': 'Rapido',
                'dni': '47555666',
                'email': 'reingreso.rapido@test.com',
                'profile_type': 'VISITOR'
            }
        }
        response = self.client.post('/api/registro-rapido/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 201)

        acreds = list(Acreditacion.objects.filter(inscripcion=inscripcion).order_by('fecha_acreditacion'))
        self.assertEqual(len(acreds), 2)
        self.assertFalse(acreds[0].es_reingreso)
        self.assertTrue(acreds[1].es_reingreso)


class BatchQueueResilienceAndSchedulerTests(TestCase):
    def setUp(self):
        self.edicion, _ = Edicion.objects.get_or_create(
            anio=2026,
            defaults={'nombre': "Congreso de Logística 2026", 'activa': True}
        )
        if not self.edicion.activa:
            self.edicion.activa = True
            self.edicion.save()

        self.admin_user = User.objects.create_superuser(
            username='admin_scheduler',
            email='admin_scheduler@unab.edu.ar',
            password='password123'
        )
        self.client.login(username='admin_scheduler', password='password123')

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_batch_avoids_head_of_line_blocking_on_failed_certs(self, mock_send):
        """
        Verifica que si el primer certificado falla (intentos=1), el siguiente lote
        avance con los restantes sin intentar (intentos=0) en vez de quedar atrapado
        en un bucle infinito sobre el certificado fallido.
        """
        certs = []
        for i in range(4):
            a = Asistente.objects.create(
                first_name=f"Batch_{i}",
                last_name="User",
                dni=f"5011122{i}",
                email=f"batch_user_{i}@gmail.com",
                profile_type="VISITOR"
            )
            certs.append(Certificado.objects.create(asistente=a, edicion=self.edicion, tipo_certificado="ASISTENCIA"))

        # Lote 1 (tamaño 2): el primero falla, el segundo tiene éxito
        mock_send.side_effect = [Exception("SMTP Temporary Error"), True]
        url = reverse('admin:process-certificate-batch') + '?batch_size=2&forzar=true&delay=0'
        res1 = self.client.get(url).json()
        self.assertEqual(res1['processed'], 1)
        self.assertEqual(res1['errors'], 1)
        self.assertEqual(res1['remaining'], 3)
        self.assertEqual(res1['remaining_unattempted'], 2)
        self.assertEqual(res1['failed_count'], 1)

        # Lote 2 (tamaño 2): debe procesar los certificados 3 y 4 (intentos=0), sin re-procesar el 1
        mock_send.side_effect = [True, True]
        res2 = self.client.get(url).json()
        self.assertEqual(res2['processed'], 2)
        self.assertEqual(res2['errors'], 0)
        self.assertEqual(res2['remaining'], 1)
        self.assertEqual(res2['remaining_unattempted'], 0)
        self.assertEqual(res2['failed_count'], 1)

        # Modo reintentar_fallidos=true: ahora sí reintenta el certificado 1 y lo envía
        mock_send.side_effect = [True]
        url_retry = url + '&reintentar_fallidos=true'
        res3 = self.client.get(url_retry).json()
        self.assertEqual(res3['processed'], 1)
        self.assertEqual(res3['remaining'], 0)
        self.assertEqual(res3['failed_count'], 0)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_sincronizar_certificados_asistencia_enqueues_missing_certs(self, mock_send):
        """
        Verifica que una inscripción con asistencia_confirmada=True sin registro Certificado
        sea sincronizada automáticamente al consultar la cola o procesar un lote.
        """
        mock_send.return_value = True
        asist = Asistente.objects.create(
            first_name="Sincronizado",
            last_name="Auto",
            dni="51222333",
            email="sincronizado@unab.edu.ar",
            profile_type="STUDENT"
        )
        Inscripcion.objects.create(
            asistente=asist,
            edicion=self.edicion,
            asistencia_confirmada=True,
            fecha_confirmacion=timezone.now()
        )
        self.assertEqual(Certificado.objects.filter(asistente=asist).count(), 0)

        url = reverse('admin:process-certificate-batch') + '?batch_size=5&forzar=true&delay=0'
        res = self.client.get(url).json()
        self.assertEqual(res['status'], 'ok')
        self.assertEqual(res['processed'], 1)

        cert = Certificado.objects.filter(asistente=asist).first()
        self.assertIsNotNone(cert)
        self.assertTrue(cert.email_enviado)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_scheduler_processes_certificates_and_keeps_backups_manual_only(self, mock_send):
        """
        Verifica que el scheduler autónomo NO ejecute respaldos automáticos (ya que los respaldos
        son exclusivamente manuales) y procese únicamente los lotes de certificados pendientes
        después de las 18:00 hs.
        """
        import datetime
        from zoneinfo import ZoneInfo
        from api.models import ConfiguracionRespaldo
        from api.scheduler import ejecutar_ciclo_scheduler

        mock_send.return_value = True
        config = ConfiguracionRespaldo.get_solo()
        config.ultimo_respaldo_fecha = None
        config.save()

        asist = Asistente.objects.create(
            first_name="Auto",
            last_name="Cert",
            dni="52333444",
            email="autocert@unab.edu.ar",
            profile_type="VISITOR"
        )
        Certificado.objects.create(asistente=asist, edicion=self.edicion, tipo_certificado="ASISTENCIA")

        tz = ZoneInfo('America/Argentina/Buenos_Aires')
        hora_post_cierre = datetime.datetime(2026, 11, 7, 19, 30, 0, tzinfo=tz)

        res = ejecutar_ciclo_scheduler(ahora_local=hora_post_cierre, batch_size=5, delay_seconds=0)
        self.assertEqual(res['status'], 'ok')
        self.assertFalse(res['backup']['executed'])
        self.assertEqual(res['backup']['reason'], 'manual_only')
        self.assertTrue(res['certificates']['executed'])

        # Verifica que ningún respaldo automático se haya disparado
        config.refresh_from_db()
        self.assertIsNone(config.ultimo_respaldo_fecha)

        # Un segundo ciclo inmediato no debe re-enviar certificados ya enviados
        res2 = ejecutar_ciclo_scheduler(ahora_local=hora_post_cierre, batch_size=5, delay_seconds=0)
        self.assertFalse(res2['backup']['executed'])
        self.assertFalse(res2['certificates']['executed'])

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_respaldos_admin_view_checkbox_and_enviar_ahora(self, mock_send):
        """
        Verifica que en /admin/respaldos/ se guarden las casillas para respaldo manual
        y que 'enviar_ahora' funcione siempre bajo demanda.
        """
        import os
        from django.conf import settings
        from api.models import ConfiguracionRespaldo

        mock_send.return_value = True
        config = ConfiguracionRespaldo.get_solo()

        res_save = self.client.post('/admin/respaldos/', {
            'accion': 'guardar',
            'email_personal': 'echavarrialucas1986@gmail.com',
            'email_institucional': 'congresologisticaytransporte@unab.edu.ar',
        })
        self.assertEqual(res_save.status_code, 302)
        config.refresh_from_db()
        self.assertFalse(config.activo)

        # Enviar respaldo manual ahora
        res_send = self.client.post('/admin/respaldos/', {
            'accion': 'enviar_ahora',
            'email_personal': 'echavarrialucas1986@gmail.com',
            'email_institucional': 'congresologisticaytransporte@unab.edu.ar',
        })
        self.assertEqual(res_send.status_code, 302)
        config.refresh_from_db()
        self.assertIsNotNone(config.ultimo_respaldo_archivo)
        zip_path = os.path.join(settings.BASE_DIR, 'backups', config.ultimo_respaldo_archivo)
        if os.path.exists(zip_path):
            os.remove(zip_path)

    def test_batch_smtp_connection_failure_does_not_falsely_mark_email_enviado(self):
        """
        Verifica que si el backend SMTP real falla (OSError o SMTPException en conexión compartida),
        NO se silencie el error con fail_silently=True ni se marque falsamente email_enviado=True.
        """
        import smtplib
        from django.test import override_settings
        from api.models import LogEnvioEmail

        asist = Asistente.objects.create(
            first_name="RealSMTP",
            last_name="Fail",
            dni="53444555",
            email="realsmtp@unab.edu.ar",
            profile_type="VISITOR"
        )
        cert = Certificado.objects.create(asistente=asist, edicion=self.edicion, tipo_certificado="ASISTENCIA")

        with override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'):
            with patch('smtplib.SMTP_SSL', side_effect=smtplib.SMTPException("454 4.7.0 Quota exceeded")):
                url = reverse('admin:process-certificate-batch') + '?batch_size=5&forzar=true&delay=0'
                res = self.client.get(url).json()

        self.assertEqual(res['status'], 'ok')
        self.assertEqual(res['processed'], 0)
        self.assertEqual(res['errors'], 1)

        cert.refresh_from_db()
        self.assertFalse(cert.email_enviado)
        self.assertEqual(cert.intentos, 1)
        log = LogEnvioEmail.objects.filter(destinatario="realsmtp@unab.edu.ar").first()
        self.assertIsNotNone(log)
        self.assertFalse(log.exitoso)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_retry_failed_cursor_advances_past_still_failing_batches(self, mock_send):
        """
        Verifica que en modo reintentar_fallidos=true con cursor after_id, si la primera tanda
        vuelve a fallar por completo (processed=0, errors=2), el cursor avance a la segunda tanda
        y envíe los certificados posteriores sin detenerse prematuramente ni repetir los ya intentados.
        """
        certs = []
        for i in range(4):
            a = Asistente.objects.create(
                first_name=f"RetryCursor_{i}",
                last_name="User",
                dni=f"5455566{i}",
                email=f"retry_cursor_{i}@gmail.com",
                profile_type="VISITOR"
            )
            certs.append(
                Certificado.objects.create(
                    asistente=a,
                    edicion=self.edicion,
                    tipo_certificado="ASISTENCIA",
                    email_enviado=False,
                    intentos=1
                )
            )

        # Tanda 1 de reintento (batch_size=2, after_id=0): ambos fallan de nuevo
        mock_send.side_effect = [Exception("Still failing 1"), Exception("Still failing 2")]
        url1 = reverse('admin:process-certificate-batch') + '?batch_size=2&forzar=true&delay=0&reintentar_fallidos=true&after_id=0'
        res1 = self.client.get(url1).json()
        self.assertEqual(res1['processed'], 0)
        self.assertEqual(res1['errors'], 2)
        self.assertEqual(res1['remaining_retry'], 2)
        self.assertEqual(res1['last_processed_id'], certs[1].id)

        # Tanda 2 de reintento (batch_size=2, after_id=last_processed_id): los siguientes 2 tienen éxito
        mock_send.side_effect = [True, True]
        url2 = reverse('admin:process-certificate-batch') + f"?batch_size=2&forzar=true&delay=0&reintentar_fallidos=true&after_id={res1['last_processed_id']}"
        res2 = self.client.get(url2).json()
        self.assertEqual(res2['processed'], 2)
        self.assertEqual(res2['errors'], 0)
        self.assertEqual(res2['remaining_retry'], 0)
        self.assertEqual(res2['remaining'], 2)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    @patch('django.utils.timezone.localtime')
    def test_post_closing_date_nov8_after_midnight_is_not_blocked_by_time(self, mock_localtime, mock_send):
        """
        Verifica que en fechas posteriores al cierre del 7 de noviembre (ej. 8 de noviembre a las 00:15 hs),
        el horario ya se considere habilitado aunque hour < 18, tanto en la API como en el scheduler.
        """
        import datetime
        from zoneinfo import ZoneInfo
        from api.scheduler import es_horario_habilitado_certificados, verificar_y_procesar_cola_certificados

        mock_send.return_value = True
        hora_madrugada_nov8 = datetime.datetime(2026, 11, 8, 0, 15, 0, tzinfo=ZoneInfo('America/Argentina/Buenos_Aires'))
        mock_localtime.return_value = hora_madrugada_nov8

        self.assertTrue(es_horario_habilitado_certificados(hora_madrugada_nov8))

        asist = Asistente.objects.create(
            first_name="Madrugada",
            last_name="Nov8",
            dni="55666777",
            email="madrugada.nov8@unab.edu.ar",
            profile_type="VISITOR"
        )
        Certificado.objects.create(asistente=asist, edicion=self.edicion, tipo_certificado="ASISTENCIA")

        # API sin forzar=true en madrugada del 8 de noviembre debe procesar sin bloquear
        url = reverse('admin:process-certificate-batch') + '?batch_size=5&forzar=false&delay=0'
        res = self.client.get(url).json()
        self.assertEqual(res['status'], 'ok')
        self.assertEqual(res['processed'], 1)

        # Scheduler en madrugada del 8 de noviembre también debe estar habilitado
        res_sched = verificar_y_procesar_cola_certificados(ahora_local=hora_madrugada_nov8, batch_size=5, delay_seconds=0)
        self.assertNotEqual(res_sched.get('reason'), 'before_18hs')

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_respaldo_reports_smtp_failure_accurately(self, mock_send):
        """
        Verifica que si el envío SMTP del respaldo falla, ejecutar_respaldo_programado
        retorne emails_enviados=[] y registre el fallo en emails_fallidos.
        """
        import os
        from api.backup_service import ejecutar_respaldo_programado

        mock_send.side_effect = Exception("SMTP Auth Error")
        res = ejecutar_respaldo_programado(destinos_forzados=['test_fail@unab.edu.ar'])
        self.assertEqual(res['status'], 'ok')
        self.assertEqual(res['emails_enviados'], [])
        self.assertEqual(len(res['emails_fallidos']), 1)

        zip_path = res.get('zip_path')
        if zip_path and os.path.exists(zip_path):
            os.remove(zip_path)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_certificate_queue_status_api_returns_live_counters_and_logs(self, mock_send):
        """
        Verifica que /admin/certificate-queue-status/ devuelva en tiempo real los contadores
        de PostgreSQL y los logs de transmisión desde LogEnvioEmail (con soporte de since_log_id)
        para renderizar el proceso en la consola de /admin/certificate-queue/.
        """
        mock_send.return_value = True
        asist = Asistente.objects.create(
            first_name="Consola",
            last_name="Live",
            dni="56777888",
            email="consola.live@unab.edu.ar",
            profile_type="VISITOR"
        )
        Certificado.objects.create(asistente=asist, edicion=self.edicion, tipo_certificado="ASISTENCIA")

        status_url = reverse('admin:certificate-queue-status')
        res_before = self.client.get(status_url).json()
        self.assertEqual(res_before['status'], 'ok')
        self.assertEqual(res_before['remaining'], 1)
        self.assertEqual(res_before['pendientes_asistencia'], 1)

        # Ejecutar lote en segundo plano y luego consultar status API con since_log_id
        from api.tasks import task_procesar_cola_certificados_lote
        task_procesar_cola_certificados_lote(batch_size=5, forzar=True, delay_seconds=0)

        res_after = self.client.get(status_url + f"?since_log_id={res_before['last_log_id']}").json()
        self.assertEqual(res_after['status'], 'ok')
        self.assertEqual(res_after['remaining'], 0)
        self.assertEqual(res_after['sent_total'], 1)
        self.assertEqual(len(res_after['recent_logs']), 1)
        self.assertIn("consola.live@unab.edu.ar", res_after['recent_logs'][0]['message'])
        self.assertEqual(res_after['recent_logs'][0]['level'], 'success')

    def test_pg_lock_coordination_prevents_overlap_between_web_and_background(self):
        """
        Verifica que si el bloqueo de PostgreSQL / cola está tomado por un proceso,
        process_certificate_batch_api retorne status='busy_background' sin duplicar envíos
        y task_procesar_cola_certificados_lote ceda prioridad con status='busy_web_or_worker'.
        """
        from api.scheduler import acquire_certificate_queue_lock
        from api.tasks import task_procesar_cola_certificados_lote

        asist = Asistente.objects.create(
            first_name="Lock",
            last_name="Coord",
            dni="57888999",
            email="lock.coord@unab.edu.ar",
            profile_type="VISITOR"
        )
        Certificado.objects.create(asistente=asist, edicion=self.edicion, tipo_certificado="ASISTENCIA")

        with acquire_certificate_queue_lock() as acquired:
            self.assertTrue(acquired)
            # Mientras el lock está activo, la API web reporta busy_background sin error
            url = reverse('admin:process-certificate-batch') + '?batch_size=5&forzar=true&delay=0'
            res_web = self.client.get(url).json()
            self.assertEqual(res_web['status'], 'busy_background')
            self.assertEqual(res_web['processed'], 0)
            self.assertEqual(res_web['remaining'], 1)

            # Y la tarea de fondo cede prioridad
            res_task = task_procesar_cola_certificados_lote(batch_size=5, forzar=True, delay_seconds=0)
            self.assertEqual(res_task['status'], 'busy_web_or_worker')
            self.assertEqual(res_task['processed'], 0)

    def test_celery_task_respaldo_programado_rejects_automatic_execution_unless_manual_true(self):
        """
        Verifica que task_ejecutar_respaldo_programado rechace ejecuciones automáticas (manual=False)
        para evitar que un Celery Beat antiguo o persistido en BD dispare respaldos programados,
        y que limpiar_tareas_respaldo_programadas_db limpie tareas huérfanas.
        """
        from api.tasks import task_ejecutar_respaldo_programado
        from api.scheduler import limpiar_tareas_respaldo_programadas_db

        res_auto = task_ejecutar_respaldo_programado()
        self.assertEqual(res_auto['status'], 'skipped')
        self.assertFalse(res_auto['ok'])
        self.assertEqual(res_auto['reason'], 'manual_only')

        # Verificar que limpiar_tareas_respaldo_programadas_db sea seguro e idempotente
        eliminadas = limpiar_tareas_respaldo_programadas_db()
        self.assertGreaterEqual(eliminadas, 0)

    def test_sql_snapshot_fallback_includes_many_to_many_tables(self):
        """
        Verifica que _generar_sql_snapshot_fallback incluya tablas intermedias ManyToMany
        (como api_programa_disertantes) en el archivo .sql del respaldo manual.
        """
        import os
        import datetime
        import tempfile
        from api.models import Disertante, Programa
        from api.backup_service import _generar_sql_snapshot_fallback

        dis = Disertante.objects.create(
            nombre="Dra. Ana Logística",
            edicion=self.edicion,
            estado='CONFIRMADO'
        )
        prog = Programa.objects.create(
            titulo="IA en Transporte",
            aula="Aula Magna",
            hora_inicio=datetime.time(10, 0),
            hora_fin=datetime.time(11, 0),
            edicion=self.edicion,
        )
        prog.disertantes.add(dis)

        with tempfile.NamedTemporaryFile(suffix='.sql', delete=False) as tmp:
            sql_path = tmp.name

        try:
            ok = _generar_sql_snapshot_fallback(sql_path)
            self.assertTrue(ok)
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            self.assertIn('api_programa_disertantes', sql_content)
        finally:
            if os.path.exists(sql_path):
                os.remove(sql_path)

    def test_postgresql_advisory_lock_acquisition_and_release_mocked(self):
        """
        Verifica el comportamiento de acquire_certificate_queue_lock cuando connection.vendor == 'postgresql':
        - Si pg_try_advisory_lock(20261107) devuelve True, adquiere el bloqueo y al salir ejecuta pg_advisory_unlock(20261107).
        - Si pg_try_advisory_lock(20261107) devuelve False, cede inmediatamente (yield False) y NO ejecuta pg_advisory_unlock.
        """
        from unittest.mock import MagicMock
        from django.db import connection
        from api.scheduler import acquire_certificate_queue_lock

        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = False

        # Caso 1: pg_try_advisory_lock devuelve True
        mock_cursor.fetchone.return_value = (True,)
        with patch.object(connection, 'vendor', 'postgresql'), patch.object(connection, 'cursor', return_value=mock_cursor):
            with acquire_certificate_queue_lock() as acquired:
                self.assertTrue(acquired)

        calls = [c[0][0] for c in mock_cursor.execute.call_args_list]
        self.assertIn("SELECT pg_try_advisory_lock(%s)", calls)
        self.assertIn("SELECT pg_advisory_unlock(%s)", calls)

        # Caso 2: pg_try_advisory_lock devuelve False (otro worker PostgreSQL tiene el lock)
        mock_cursor.reset_mock()
        mock_cursor.fetchone.return_value = (False,)
        with patch.object(connection, 'vendor', 'postgresql'), patch.object(connection, 'cursor', return_value=mock_cursor):
            with acquire_certificate_queue_lock() as acquired:
                self.assertFalse(acquired)

        calls_busy = [c[0][0] for c in mock_cursor.execute.call_args_list]
        self.assertIn("SELECT pg_try_advisory_lock(%s)", calls_busy)
        self.assertNotIn("SELECT pg_advisory_unlock(%s)", calls_busy)

    def test_web_console_priority_lifecycle(self):
        """Verifica el ciclo de vida de la reserva de prioridad de la consola web (mark, check, clear)."""
        from api.scheduler import mark_web_console_priority, is_web_console_priority_active, clear_web_console_priority

        clear_web_console_priority()
        self.assertFalse(is_web_console_priority_active())

        mark_web_console_priority(ttl_seconds=10.0)
        self.assertTrue(is_web_console_priority_active())

        clear_web_console_priority()
        self.assertFalse(is_web_console_priority_active())

    def test_cron_window_yields_to_web_console_priority(self):
        """La ventana de cron debe ceder inmediatamente si la consola web tiene prioridad activa."""
        from api.scheduler import mark_web_console_priority, clear_web_console_priority, ejecutar_ventana_cron_scheduler

        try:
            mark_web_console_priority(ttl_seconds=25.0)
            res = ejecutar_ventana_cron_scheduler(max_seconds=5.0)
            self.assertEqual(res['status'], 'yielded_to_web_console')
            self.assertEqual(res['reason'], 'web_console_priority')
            self.assertEqual(res['batches_run'], 0)
        finally:
            clear_web_console_priority()

    def test_backup_zip_rotation_preserves_maximum_10_files(self):
        """Verifica que generar_paquete_backup() rote los paquetes y conserve como máximo los últimos 10 .zip."""
        import os
        import time
        from django.conf import settings
        from api.backup_service import generar_paquete_backup

        backups_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backups_dir, exist_ok=True)

        created_dummy_zips = []
        try:
            # Crear 14 archivos dummy con marcas de tiempo escalonadas
            base_time = time.time() - 3600
            for i in range(14):
                dummy_name = f"backup_congreso_20261108_{i:06d}.zip"
                dummy_path = os.path.join(backups_dir, dummy_name)
                with open(dummy_path, 'wb') as f:
                    f.write(b"dummy zip content")
                os.utime(dummy_path, (base_time + i * 10, base_time + i * 10))
                created_dummy_zips.append(dummy_path)

            zip_path, zip_name, size_bytes = generar_paquete_backup()
            created_dummy_zips.append(zip_path)

            existing_zips = [
                f for f in os.listdir(backups_dir)
                if f.startswith('backup_congreso_') and f.endswith('.zip')
            ]
            self.assertLessEqual(len(existing_zips), 10)
            self.assertIn(zip_name, existing_zips)
        finally:
            for p in created_dummy_zips:
                try:
                    if os.path.exists(p):
                        os.remove(p)
                except OSError:
                    pass

    def test_sincronizar_certificados_normalizes_edicion_none_and_prevents_duplicate(self):
        """Verifica que certificados con edicion=None se normalicen a la edicion_activa y no se dupliquen."""
        from api.services import sincronizar_certificados_asistencia

        asist = Asistente.objects.create(
            first_name="Norm",
            last_name="Edicion",
            email="norm.edicion@unab.edu.ar",
            dni="88990011",
            profile_type="VISITOR"
        )
        Inscripcion.objects.create(
            asistente=asist,
            edicion=self.edicion,
            asistencia_confirmada=True
        )

        # Crear certificado sin edición asignada
        cert_sin_edicion = Certificado.objects.create(
            asistente=asist,
            edicion=None,
            tipo_certificado="ASISTENCIA",
            email_enviado=False
        )

        nuevos = sincronizar_certificados_asistencia()
        self.assertEqual(nuevos, 0)

        cert_sin_edicion.refresh_from_db()
        self.assertEqual(cert_sin_edicion.edicion, self.edicion)
        self.assertEqual(Certificado.objects.filter(asistente=asist).count(), 1)

        # Simular que se envió el certificado
        cert_sin_edicion.email_enviado = True
        cert_sin_edicion.save(update_fields=['email_enviado'])

        # Sincronizar de nuevo: NO debe crear duplicado a pesar de que email_enviado=True
        nuevos_segunda_vez = sincronizar_certificados_asistencia()
        self.assertEqual(nuevos_segunda_vez, 0)
        self.assertEqual(Certificado.objects.filter(asistente=asist).count(), 1)

    def test_is_certificate_queue_locked_postgresql_idle_filtering(self):
        """Verifica que is_certificate_queue_locked() filtre sesiones idle > 35s en PostgreSQL."""
        from unittest.mock import MagicMock
        from django.db import connection
        from api.scheduler import is_certificate_queue_locked

        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = False
        mock_cursor.fetchone.return_value = (True,)

        with patch.object(connection, 'vendor', 'postgresql'), patch.object(connection, 'cursor', return_value=mock_cursor):
            is_locked = is_certificate_queue_locked()
            self.assertTrue(is_locked)

        calls = [c[0][0] for c in mock_cursor.execute.call_args_list]
        self.assertTrue(any("state_change > (now() - interval '35 seconds')" in q for q in calls))

    def test_is_certificate_queue_locked_postgresql_does_not_acquire_file_lock(self):
        """
        Verifica que en PostgreSQL, is_certificate_queue_locked() consulte directamente pg_locks
        sin adquirir el bloqueo de archivo local, previniendo contención de locks durante polling HTTP.
        """
        from unittest.mock import MagicMock
        from django.db import connection
        from api.scheduler import is_certificate_queue_locked

        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = False
        mock_cursor.fetchone.return_value = (False,)

        with patch.object(connection, 'vendor', 'postgresql'), \
             patch.object(connection, 'cursor', return_value=mock_cursor), \
             patch('api.scheduler._acquire_file_lock') as mock_file_lock:
            locked = is_certificate_queue_locked()
            self.assertFalse(locked)
            mock_file_lock.assert_not_called()

    def test_acquire_certificate_queue_lock_closes_connection_on_unlock_failure(self):
        """
        Verifica que ante un fallo liberando el advisory lock en PostgreSQL (ej. conexión abortada),
        se cierre explícitamente la conexión para forzar la liberación de advisory locks en PgBouncer.
        """
        from unittest.mock import MagicMock
        from django.db import connection
        from api.scheduler import acquire_certificate_queue_lock

        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = False
        mock_cursor.fetchone.return_value = (True,)
        mock_cursor.fetchall.return_value = []

        def execute_side_effect(sql, params=None):
            if "SELECT pg_advisory_unlock" in str(sql):
                raise Exception("DB Connection Lost during unlock")
            return None

        mock_cursor.execute.side_effect = execute_side_effect

        with patch.object(connection, 'vendor', 'postgresql'), \
             patch.object(connection, 'cursor', return_value=mock_cursor), \
             patch.object(connection, 'close') as mock_close:
            with acquire_certificate_queue_lock() as acquired:
                self.assertTrue(acquired)
                mock_close.reset_mock()
            mock_close.assert_called_once()

    def test_mark_web_console_priority_cleans_fallback_on_primary_success(self):
        """Verifica que al registrar prioridad en path primario, se limpie cualquier fallback previo."""
        import os
        from api.scheduler import _get_web_console_priority_paths, mark_web_console_priority, clear_web_console_priority

        paths = _get_web_console_priority_paths()
        primary, fallback = paths[0], paths[1]

        try:
            # Crear fallback previo
            with open(fallback, 'w', encoding='utf-8') as f:
                f.write('9999999999')
            self.assertTrue(os.path.exists(fallback))

            mark_web_console_priority(ttl_seconds=15.0)
            self.assertTrue(os.path.exists(primary))
            self.assertFalse(os.path.exists(fallback))
        finally:
            clear_web_console_priority()

    def test_obtener_lista_certificados_fallidos_includes_error_motivo(self):
        """
        Verifica que obtener_lista_certificados_fallidos() liste con precisión cada certificado
        fallido (intentos > 0, email_enviado=False) junto con su participante y el motivo exacto del fallo
        (typo de dominio, error de sintaxis o error de transporte SMTP registrado en LogEnvioEmail).
        """
        from api.scheduler import obtener_lista_certificados_fallidos
        from api.models import LogEnvioEmail

        # Participante con typo en dominio (@gmial.com)
        asist_typo = Asistente.objects.create(
            first_name="Carlos",
            last_name="Typo",
            dni="44111222",
            email="carlos.typo@gmial.com",
            profile_type="VISITOR"
        )
        cert_typo = Certificado.objects.create(
            asistente=asist_typo,
            edicion=self.edicion,
            tipo_certificado="ASISTENCIA",
            email_enviado=False,
            intentos=1
        )

        # Participante con error SMTP en LogEnvioEmail
        asist_smtp = Asistente.objects.create(
            first_name="Elena",
            last_name="Smtp",
            dni="44333444",
            email="elena.smtp@gmail.com",
            profile_type="VISITOR"
        )
        cert_smtp = Certificado.objects.create(
            asistente=asist_smtp,
            edicion=self.edicion,
            tipo_certificado="DISERTANTE",
            email_enviado=False,
            intentos=2
        )
        LogEnvioEmail.objects.create(
            destinatario="elena.smtp@gmail.com",
            asunto="Certificado de Disertante",
            tipo_email="certificado_disertante",
            exitoso=False,
            error="Fallo en PDF o SMTP: 454 4.7.0 Demasiados envíos concurrentes"
        )

        fallidos = obtener_lista_certificados_fallidos(limit=10)
        fallidos_dict = {f['id']: f for f in fallidos}

        self.assertIn(cert_typo.id, fallidos_dict)
        self.assertIn(cert_smtp.id, fallidos_dict)

        self.assertIn("gmial.com", fallidos_dict[cert_typo.id]['error'].lower())
        self.assertEqual(fallidos_dict[cert_typo.id]['nombre'], "Carlos Typo")
        self.assertEqual(fallidos_dict[cert_typo.id]['dni'], "44111222")
        self.assertEqual(fallidos_dict[cert_typo.id]['intentos'], 1)

        self.assertIn("454 4.7.0", fallidos_dict[cert_smtp.id]['error'])
        self.assertEqual(fallidos_dict[cert_smtp.id]['nombre'], "Elena Smtp")
        self.assertEqual(fallidos_dict[cert_smtp.id]['tipo'], "DISERTANTE")
        self.assertEqual(fallidos_dict[cert_smtp.id]['intentos'], 2)

    def test_certificate_queue_view_export_fallidos_excel(self):
        """
        Verifica que al acceder a /admin/certificate-queue/?descargar=fallidos_excel
        se genere y retorne un archivo Excel (.xlsx) con la lista de certificados fallidos.
        """
        asist = Asistente.objects.create(
            first_name="Export",
            last_name="Test",
            dni="44999888",
            email="export.test@gmial.com",
            profile_type="VISITOR"
        )
        Certificado.objects.create(
            asistente=asist,
            edicion=self.edicion,
            tipo_certificado="ASISTENCIA",
            email_enviado=False,
            intentos=1
        )

        url = reverse('admin:admin-certificate-queue') + '?descargar=fallidos_excel'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertIn('attachment; filename="certificados_fallidos_', response['Content-Disposition'])
        self.assertTrue(len(response.content) > 1000)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_reintentar_certificado_individual_api(self, mock_send):
        """
        Verifica que el endpoint /admin/certificate-queue/reintentar/<id>/
        reinicie el contador de intentos a 0 o envíe de inmediato el certificado individual.
        """
        mock_send.return_value = True
        asist = Asistente.objects.create(
            first_name="Reintentar",
            last_name="Single",
            dni="44777888",
            email="reintentar.single@gmail.com",
            profile_type="VISITOR"
        )
        cert = Certificado.objects.create(
            asistente=asist,
            edicion=self.edicion,
            tipo_certificado="ASISTENCIA",
            email_enviado=False,
            intentos=3
        )

        # 1. Reinicio simple sin envío inmediato
        url = reverse('admin:admin-certificate-reintentar-individual', args=[cert.id])
        res = self.client.post(url).json()
        self.assertEqual(res['status'], 'ok')
        cert.refresh_from_db()
        self.assertEqual(cert.intentos, 0)
        self.assertFalse(cert.email_enviado)

        # 2. Reintento con envío inmediato
        cert.intentos = 2
        cert.save()
        res_send = self.client.post(url + '?enviar_ahora=1').json()
        self.assertEqual(res_send['status'], 'ok')
        self.assertTrue(res_send['success'])
        cert.refresh_from_db()
        self.assertTrue(cert.email_enviado)





