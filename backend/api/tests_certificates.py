from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch, MagicMock
from api.models import Asistente, Certificado, Edicion, Inscripcion
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

        # Limpieza
        if os.path.exists(zip_path):
            os.remove(zip_path)

    def test_celery_beat_schedule_five_slots_configured(self):
        """
        Valida que settings.CELERY_BEAT_SCHEDULE tenga registrados los 5 horarios exactos
        estipulados para el Congreso de Logística:
        - Viernes 6 Nov a las 23:59 hs
        - Sábado 7 Nov a las 06:00, 10:00, 14:00 y 18:00 hs
        """
        from django.conf import settings
        sched = settings.CELERY_BEAT_SCHEDULE

        claves_esperadas = [
            'respaldo-sistema-viernes-2359',
            'respaldo-sistema-sabado-0600',
            'respaldo-sistema-sabado-1000',
            'respaldo-sistema-sabado-1400',
            'respaldo-sistema-sabado-1800',
        ]
        for k in claves_esperadas:
            self.assertIn(k, sched, f"Falta clave de cronograma {k} en CELERY_BEAT_SCHEDULE")
            self.assertEqual(sched[k]['task'], 'api.tasks.task_ejecutar_respaldo_programado')

        # Validar crontab específico de viernes 23:59
        cron_v = sched['respaldo-sistema-viernes-2359']['schedule']
        self.assertIn(59, cron_v.minute)
        self.assertIn(23, cron_v.hour)
        self.assertIn(6, cron_v.day_of_month)

        # Validar crontab de sábado 06:00
        cron_s6 = sched['respaldo-sistema-sabado-0600']['schedule']
        self.assertIn(0, cron_s6.minute)
        self.assertIn(6, cron_s6.hour)
        self.assertIn(7, cron_s6.day_of_month)

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

    def test_admin_respaldos_descarga_directa_zip(self):
        """
        Valida que el endpoint de admin /admin/respaldos/?descargar=zip retorne
        el stream del archivo ZIP con los headers HTTP correctos.
        """
        from django.contrib.auth.models import User
        admin_user, _ = User.objects.get_or_create(username='admin_respaldo_test', is_staff=True, is_superuser=True)
        self.client.force_login(admin_user)

        response = self.client.get('/admin/respaldos/?descargar=zip')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertIn('attachment; filename="backup_congreso_', response['Content-Disposition'])






