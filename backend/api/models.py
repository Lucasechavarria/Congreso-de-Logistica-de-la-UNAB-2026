from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from django.core.files.storage import storages
from django.core.exceptions import ValidationError
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.utils import timezone
import re


class Disertante(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    edicion = models.ForeignKey('Edicion', on_delete=models.CASCADE, null=True, blank=True, related_name='disertantes')
    ESTADO_CHOICES = [('PENDIENTE', 'Pendiente'), ('APROBADO', 'Aprobado'), ('RECHAZADO', 'Rechazado')]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado")
    nombre = models.CharField(max_length=200)
    bio = models.TextField(verbose_name="Biografía")
    foto_url = models.CharField(max_length=300, blank=True, verbose_name="URL de la Foto")
    foto = models.ImageField(upload_to='ponencias/', blank=True, null=True, verbose_name="Foto (subida)")
    linkedin = models.CharField(max_length=500, blank=True, null=True, verbose_name='Perfil de LinkedIn')
    tema_presentacion = models.CharField(max_length=255, verbose_name="Título de la Presentación")

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']

class PostulacionDisertante(models.Model):
    edicion = models.ForeignKey('Edicion', on_delete=models.CASCADE, null=True, blank=True, related_name='postulaciones_disertantes')
    # Personal & Profesional
    nombre_apellido = models.CharField(max_length=200, verbose_name="Nombre y Apellido")
    dni = models.CharField(max_length=8, db_index=True, verbose_name="DNI / Documento")
    email = models.EmailField(verbose_name="Email de contacto")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    ciudad_provincia = models.CharField(max_length=255, verbose_name="Ciudad y Provincia")
    profesion_cargo = models.CharField(max_length=255, verbose_name="Profesión / Cargo actual")
    empresa_institucion = models.CharField(max_length=255, verbose_name="Empresa / Institución a la que pertenece")
    linkedin = models.CharField(max_length=500, blank=True, null=True, verbose_name="LinkedIn u otra red profesional")
    
    # Propuesta de Charla
    titulo_charla = models.CharField(max_length=255, verbose_name="Título de la exposición")
    ejes_tematicos = models.TextField(default='', blank=True, verbose_name="Eje temático al que se vincula (JSON String)")
    eje_otro = models.TextField(blank=True, null=True, verbose_name="Otro eje temático")
    resumen_charla = models.TextField(verbose_name="Resumen de la charla (máx. 300 palabras)")
    objetivos_charla = models.TextField(verbose_name="Objetivos de la exposición")
    publico_dirigido = models.TextField(default='', verbose_name="Público al que está dirigida (JSON String)")
    
    # Modalidad y Participación
    modalidad = models.TextField(default='', verbose_name="Formato preferido (JSON String)")
    participacion_tipo = models.TextField(default='', verbose_name="Tipo de participación (JSON String)")
    
    # Aceptación
    # Detalles de la propuesta
    foto_perfil = models.FileField(upload_to='postulaciones_fotos/', null=True, blank=True, verbose_name="Foto de perfil (opcional)")
    experiencia_previa = models.TextField(null=True, blank=True, verbose_name="Experiencia previa disertando")
    duracion_estimada = models.IntegerField(default=30, verbose_name="Duración estimada (minutos)", help_text="Por defecto 30 min. Editable desde el admin.")
    requiere_equipamiento = models.TextField(null=True, blank=True, verbose_name="Equipamiento requerido (proyector, micrófono, etc.)")

    # Estado y gestión interna
    ESTADO_CHOICES = [('PENDIENTE', 'Pendiente'), ('APROBADO', 'Aprobado'), ('RECHAZADO', 'Rechazado')]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado de la postulación")
    notas_admin = models.TextField(null=True, blank=True, verbose_name="Notas internas (solo admin)")
    fecha_revision = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de revisión")
    revisada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='postulaciones_revisadas', verbose_name="Revisada por")
    acepta_tyc = models.BooleanField(default=False, verbose_name="Declaro que la información es verídica y acepto TyC")
    fecha_postulacion = models.DateTimeField(auto_now_add=True, db_index=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.nombre_apellido} - {self.titulo_charla} ({self.get_estado_display()})"

    class Meta:
        ordering = ['-fecha_postulacion']

class Programa(models.Model):
    AULA_CHOICES = [
        ("Aula Magna", "Aula Magna"),
        ("Aula 1", "Aula 1"),
        ("Aula 2", "Aula 2"),
        ("Aula 3", "Aula 3"),
        ("Aula 4", "Aula 4"),
        ("Aula 5", "Aula 5"),
        ("Aula 6", "Aula 6"),
        ("Aula 7", "Aula 7"),
        ("Aula 8", "Aula 8"),
        ("Aula 9", "Aula 9"),
        ("Aula 10", "Aula 10"),
    ]
    
    CATEGORIA_CHOICES = [
        ("TECNOLOGIA", "Tecnologia"),
        ("LOGISTICA", "Logistica"),
        ("PUERTOS/COMERCIO EXTERIOR", "Puertos/Comercio Exterior"),
        ("E-COMMERS", "E-Commers"),
        ("SUPPLY CHAIN", "Supply Chain"),
        ("CAPITAL HUMANO", "Capital Humano"),
        ("RADIO", "Radio"),
        ("SUSTENTABILIDAD", "Sustentabilidad"),
        ("TRANSPORTE", "Transporte"),
    ]
    
    edicion = models.ForeignKey('Edicion', on_delete=models.CASCADE, null=True, blank=True, related_name='programas')
    titulo = models.CharField(max_length=255, verbose_name="Título del Evento")
    disertantes = models.ManyToManyField(Disertante, blank=True, verbose_name="Disertantes", related_name="programas")
    hora_inicio = models.TimeField(verbose_name="Hora de Inicio")
    hora_fin = models.TimeField(verbose_name="Hora de Fin")
    dia = models.DateField(verbose_name="Día del Evento")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    aula = models.CharField(max_length=30, choices=AULA_CHOICES, verbose_name="Aula")
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES, default="LOGÍSTICA", verbose_name="Categoría")

    def __str__(self):
        return f"{self.titulo} - {self.dia} {self.hora_inicio}"

class Empresa(models.Model):
    edicion = models.ForeignKey('Edicion', on_delete=models.CASCADE, null=True, blank=True, related_name='empresas')
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ENVIO_BC', 'Envío de Bases y Condiciones'),
        ('PENDIENTE_PAGO', 'Pendiente de Pago'),
        ('CONFIRMADA', 'Confirmada'),
        ('RECHAZADA', 'Rechazada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado")
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Fecha de registro")
    # Main Info
    nombre_empresa = models.CharField(max_length=255, db_index=True, verbose_name="Nombre de la empresa o institución")
    cuit = models.CharField(max_length=15, blank=True, null=True, verbose_name="CUIT de la empresa")
    direccion = models.CharField(max_length=500, blank=True, null=True, verbose_name="Dirección de la empresa")
    telefono_empresa = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono de la empresa")
    email_empresa = models.EmailField(blank=True, null=True, verbose_name="Email corporativo de la empresa")
    sitio_web = models.CharField(max_length=500, blank=True, null=True, verbose_name="Sitio Web de la empresa")
    descripcion = models.TextField(blank=True, null=True, verbose_name="¿Quiénes son y a qué se dedican?")
    difusion_redes = models.TextField(blank=True, null=True, verbose_name="¿Qué les gustaría que contemos en nuestras redes de ustedes?")
    logo = models.FileField(upload_to='logos_empresas/', blank=True, null=True, verbose_name="Logo de la empresa")
    
    # Sponsor fields
    es_sponsor = models.BooleanField(default=False, verbose_name="¿Es Patrocinador?")
    youtube_video_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="URL del Video de YouTube")

    # Contact Person
    nombre_contacto = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nombre completo de la persona de contacto")
    email_contacto = models.EmailField(unique=False, blank=True, null=True, db_index=True, verbose_name="Correo electrónico de la persona de contacto")
    celular_contacto = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número de celular de contacto")
    cargo_contacto = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cargo que cumple en la empresa / institución")

    # Participation
    participacion_opciones = models.CharField(max_length=500, blank=True, null=True, verbose_name="¿Cómo les gustaría participar?")
    participacion_otra = models.CharField(max_length=255, blank=True, null=True, verbose_name="Otra forma de participación")

    # Logística y TyC
    participo_edicion_anterior = models.BooleanField(default=False, verbose_name="¿Participó en la edición anterior?")
    rubro_logistico = models.CharField(max_length=255, blank=True, null=True, verbose_name="Rubro dentro del sector logístico")
    requiere_electricidad = models.BooleanField(default=False, verbose_name="¿Requiere conexión eléctrica para TV/PC?")
    computadora_o_pantalla = models.BooleanField(default=False, verbose_name="¿Llevará pantalla o equipo audiovisual propio?")
    TIPO_MOBILIARIO_CHOICES = [
        ('Mesa y dos sillas', 'Mesa y dos sillas'),
        ('Solo mesa', 'Solo mesa'),
        ('Solo dos sillas', 'Solo dos sillas'),
        ('Ninguno', 'No requiere mobiliario'),
    ]
    tipo_mobiliario = models.CharField(max_length=50, choices=TIPO_MOBILIARIO_CHOICES, blank=True, null=True, verbose_name="¿Requiere mobiliario?")
    gazebo_propio = models.BooleanField(default=False, verbose_name="¿Cuenta con gazebo propio?")
    estructura_adicional = models.TextField(blank=True, null=True, verbose_name="Estructura adicional (back, banners, etc.)")
    acciones_stand = models.TextField(blank=True, null=True, verbose_name="Acciones de difusión/sorteos en el stand")
    acepta_tyc = models.BooleanField(default=False, verbose_name="Acepta Términos y Condiciones")

    # Gestión interna (solo admin)
    cantidad_representantes = models.IntegerField(null=True, blank=True, verbose_name="Cantidad de representantes que asistirán", help_text="Editable hasta el día del evento")
    numero_stand = models.CharField(max_length=20, null=True, blank=True, verbose_name="Número de stand asignado", help_text="Asignado y editable desde el admin")
    notas_admin = models.TextField(null=True, blank=True, verbose_name="Notas internas (solo admin)")
    fecha_revision = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de revisión")
    revisada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='empresas_revisadas', verbose_name="Revisada por")
    history = HistoricalRecords()

    def __str__(self):
        if self.nombre_empresa:
            return self.nombre_empresa
        return f"Empresa sin nombre (ID: {self.pk})"

    class Meta:
        ordering = ['nombre_empresa']

class Asistente(models.Model):
    class ProfileType(models.TextChoices):
        VISITOR = 'VISITOR', 'Visitante'
        STUDENT = 'STUDENT', 'Estudiante'
        TEACHER = 'TEACHER', 'Docente'
        PROFESSIONAL = 'PROFESSIONAL', 'Profesional'
        PRESS = 'PRESS', 'Prensa/Influencer'
        GROUP_REPRESENTATIVE = 'GROUP_REPRESENTATIVE', 'Representante de Grupo'
        GRADUADO = 'GRADUADO', 'Graduado'
        OTRO = 'OTRO', 'Otro'

    # --- Información Principal (Común a todos) ---
    first_name = models.CharField(max_length=100, db_index=True, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, db_index=True, verbose_name="Apellido")
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número de celular")
    dni = models.CharField(max_length=8, unique=True, null=True, blank=True, verbose_name="DNI")
    dni_update_token = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name="Token de actualización de DNI")
    dni_email_sent = models.BooleanField(default=False, verbose_name="Email de solicitud DNI enviado")
    dni_email_sent_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha envío email DNI")
    profile_type = models.CharField(max_length=30, choices=ProfileType.choices, verbose_name="Tipo de Perfil")
    
    # Campo adicional para roles específicos (ej: "Colaborador/a Estudiante", "Colaborador/a Docente")
    rol_especifico = models.CharField(max_length=255, blank=True, null=True, verbose_name="Rol Específico")
    comision = models.CharField(max_length=255, blank=True, null=True, verbose_name="Comisión / Curso")

    # --- Relación de Grupo ---
    representante_grupo = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='miembros_representados',
        verbose_name="Representante del Grupo"
    )

    # --- Vinculaciones para Pantallas QR (desnormalizado para velocity) ---
    empresa_vinculada = models.ForeignKey(
        'Empresa', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='representantes_asistente', verbose_name="Empresa vinculada"
    )
    disertante_vinculado = models.ForeignKey(
        'Disertante', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='asistente_disertante', verbose_name="Disertante vinculado"
    )
    prensa_vinculada = models.ForeignKey(
        'InscripcionPrensa', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='asistente_prensa', verbose_name="Inscripción prensa vinculada"
    )
    
    # --- Datos de Prensa/Influencer (para registro directo) ---
    prensa_medio = models.CharField(max_length=255, blank=True, null=True, verbose_name="Medio al que pertenece")
    prensa_links = models.TextField(blank=True, null=True, verbose_name="Links de web, redes o canales de difusión")

    # --- Información adicional ---
    ciudad_provincia = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ciudad / Provincia")
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Fecha de registro")

    # --- Términos y Condiciones ---
    terminos_aceptados = models.BooleanField(default=False, verbose_name="Acepta Términos y Condiciones")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        """Valida que el DNI tenga exactamente 8 dígitos numéricos"""
        super().clean()
        if self.dni:
            # Limpiar caracteres no numéricos
            dni_limpio = str(re.sub(r'\D', '', str(self.dni)))
            # Si tiene 9 dígitos y termina en 0, eliminar el último 0
            if len(dni_limpio) == 9 and dni_limpio.endswith('0'):
                # Eliminar el último carácter si es cero en un DNI de 9 dígitos
                dni_limpio = dni_limpio[0:8]
            # Validar que tenga exactamente 8 dígitos
            if len(dni_limpio) != 8 or not dni_limpio.isdigit():
                raise ValidationError({
                    'dni': 'El DNI debe tener exactamente 8 dígitos numéricos.'
                })
            # Actualizar el DNI limpio
            self.dni = dni_limpio

    def save(self, *args, **kwargs):
        """Limpia y valida el DNI antes de guardar"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def es_representante_grupo(self):
        """Verifica si este asistente es representante de un grupo"""
        return self.profile_type == self.ProfileType.GROUP_REPRESENTATIVE
    
    @property
    def es_miembro_grupo(self):
        """Verifica si este asistente es miembro de un grupo"""
        return self.representante_grupo is not None
    
    def get_miembros_grupo(self):
        """Obtiene todos los miembros que representa este asistente"""
        if self.es_representante_grupo:
            return self.miembros_representados.all()  # type: ignore
        return Asistente.objects.none()
    
    def get_cantidad_miembros_actual(self):
        """Obtiene la cantidad actual de miembros registrados"""
        if self.es_representante_grupo:
            return self.miembros_representados.count()  # type: ignore
        return 0

class MiembroGrupo(models.Model):
    representante = models.ForeignKey(Asistente, on_delete=models.CASCADE, related_name='miembros_grupo')
    full_name = models.CharField(max_length=200, verbose_name="Nombre completo")
    dni = models.CharField(max_length=10, verbose_name="DNI")
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Fecha de registro")

    def __str__(self):
        return f"{self.full_name} (Grupo de {self.representante})"

class Certificado(models.Model):
    class TipoCertificado(models.TextChoices):
        ASISTENCIA = 'ASISTENCIA', 'Asistencia'
        DISERTANTE = 'DISERTANTE', 'Disertante'
        EMPRESA = 'EMPRESA', 'Empresa'

    asistente = models.ForeignKey(Asistente, on_delete=models.CASCADE)
    edicion = models.ForeignKey('Edicion', on_delete=models.CASCADE, null=True, blank=True, related_name='certificados')
    tipo_certificado = models.CharField(max_length=10, choices=TipoCertificado.choices, verbose_name="Tipo de Certificado")
    pdf_generado = models.FileField(upload_to='certificados/', storage=storages["private"], blank=True, null=True, verbose_name="PDF Generado")
    fecha_generacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Generación")
    
    # --- Gestión de Envío ---
    email_enviado = models.BooleanField(default=False, verbose_name="Email Enviado")
    fecha_envio = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Envío")
    intentos = models.IntegerField(default=0, verbose_name="Intentos de Envío")

    def __str__(self):
        return f"Certificado de {self.get_tipo_certificado_display()} para {self.asistente.first_name} {self.asistente.last_name}" # type: ignore

    class Meta:
        unique_together = ('asistente', 'edicion', 'tipo_certificado')
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"

    def generar_pdf(self, save=True): # type: ignore
        """
        Genera un PDF personalizado usando la imagen base y superponiendo el nombre del asistente.
        """
        import os
        from django.conf import settings
        from django.core.files.base import ContentFile
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO

        # --- GENERACIÓN 2026: Usar fondo nuevo y limpio ---
        if self.tipo_certificado == 'DISERTANTE':
            bg_name = 'Certificados-congreso-disertantes-2026.png'
        else:
            bg_name = 'Certificados-congreso-2026.png'
            
        bg_path = os.path.join(settings.BASE_DIR, 'certificates', bg_name)
        
        try:
            img = Image.open(bg_path).convert("RGB")
        except FileNotFoundError:
            # Fallback al original si por alguna razón no existe el nuevo
            bg_path_old = os.path.join(settings.BASE_DIR, 'certificates', 'Certificados-congreso.png')
            img = Image.open(bg_path_old).convert("RGB")

        draw = ImageDraw.Draw(img)

        # Configurar fuente para el nombre (Dinámica v11)
        font_size = 70
        try:
            font_path = os.path.join(settings.BASE_DIR, 'api', 'fonts', 'DejaVu_Sans', 'DejaVuSans-Bold.ttf')
            nombre_apellido = self.asistente.nombre_completo.upper()
            
            # Bucle de escalado dinámico para nombres compuestos/largos
            while font_size > 20:
                font = ImageFont.truetype(font_path, font_size)
                bbox = draw.textbbox((0, 0), nombre_apellido, font=font)
                text_width = bbox[2] - bbox[0]
                if text_width < 1700: # Margen de seguridad (Ancho imagen 2000)
                    break
                font_size -= 5
        except Exception:
            font = ImageFont.load_default()
            nombre_apellido = self.asistente.nombre_completo.upper()
            bbox = draw.textbbox((0, 0), nombre_apellido, font=font)
            text_width = bbox[2] - bbox[0]

        x = (img.width - text_width) // 2
        y = 400  # Posición vertical v13 (Compacto - Más cerca del logo y cuerpo)
        
        # Escribir el nombre (color azul)
        draw.text((x, y), nombre_apellido, font=font, fill=(18, 90, 150, 255))

        # Convertir la imagen a PDF en memoria
        buffer = BytesIO()
        img.save(buffer, format="PDF", resolution=100.0)
        buffer.seek(0)
        
        if save:
            file_name = f"certificado_{self.asistente.email}.pdf"
            self.pdf_generado.save(file_name, ContentFile(buffer.getvalue()), save=True)
        
        return buffer


class Edicion(models.Model):
    anio = models.IntegerField(unique=True, verbose_name="Año de la Edición")
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    activa = models.BooleanField(default=False, verbose_name="¿Es la edición actual?")

    def save(self, *args, **kwargs):
        if self.activa:
            # Desactivar otras ediciones si esta es activa
            Edicion.objects.filter(activa=True).update(activa=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.anio})"

    class Meta:
        verbose_name = "Edición"
        verbose_name_plural = "Ediciones"

class DetalleEstudiante(models.Model):
    asistente = models.OneToOneField('Asistente', on_delete=models.CASCADE, related_name='detalle_estudiante')
    is_unab_student = models.BooleanField(default=False, verbose_name="¿Perteneces a la UNaB?")
    institution = models.CharField(max_length=255, blank=True, null=True, verbose_name="Institución (estudio o trabajo)")
    career = models.CharField(max_length=255, blank=True, null=True, verbose_name="Carrera que cursas")
    year_of_study = models.IntegerField(null=True, blank=True, verbose_name="Año que cursas")

class DetalleDocente(models.Model):
    asistente = models.OneToOneField('Asistente', on_delete=models.CASCADE, related_name='detalle_docente')
    institution = models.CharField(max_length=255, blank=True, null=True, verbose_name="Institución")
    career_taught = models.CharField(max_length=255, blank=True, null=True, verbose_name="Carrera que dicta")

class DetalleProfesional(models.Model):
    asistente = models.OneToOneField('Asistente', on_delete=models.CASCADE, related_name='detalle_profesional')
    work_area = models.CharField(max_length=255, blank=True, null=True, verbose_name="Área de trabajo")
    occupation = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cargo")

class DetalleGrupo(models.Model):
    asistente = models.OneToOneField('Asistente', on_delete=models.CASCADE, related_name='detalle_grupo')
    group_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nombre de la institución o grupo")
    group_municipality = models.CharField(max_length=255, blank=True, null=True, verbose_name="Partido al que pertenece la institución")
    group_size = models.IntegerField(default=0, verbose_name="Cantidad de personas en el grupo")
    institution_or_workplace = models.CharField(max_length=255, null=True, blank=True, verbose_name="Institución o lugar de trabajo del representante")
    # Checkbox multiple: ESCOLAR | UNIVERSITARIO | INSTITUCIONAL | EMPRESARIAL | OTRO
    tipo_grupo = models.TextField(default='', verbose_name="Tipo de grupo", help_text="Opciones JSON: ESCOLAR, UNIVERSITARIO, INSTITUCIONAL, EMPRESARIAL, OTRO")

class InscripcionPrensa(models.Model):
    """Registro voluntario de prensa e influencers. Sin convocatoria formal."""
    edicion = models.ForeignKey('Edicion', on_delete=models.CASCADE, null=True, blank=True, related_name='inscripciones_prensa')
    # Identidad
    nombre_apellido = models.CharField(max_length=200, verbose_name="Nombre y Apellido")
    dni = models.CharField(max_length=8, db_index=True, verbose_name="DNI")
    email = models.EmailField(verbose_name="Email de contacto")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    ciudad_provincia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ciudad / Provincia")
    # Perfil mediático
    TIPO_CHOICES = [
        ('PERIODISTA',  'Periodista / Medio de comunicación'),
        ('INFLUENCER',  'Influencer / Creador de contenido digital'),
        ('FOTOGRAFO',   'Fotógrafo / Camarógrafo'),
        ('BLOGGER',     'Blogger'),
        ('PODCASTER',   'Podcaster'),
        ('OTRO',        'Otro perfil mediático'),
    ]
    tipo_perfil = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de perfil")
    medio_o_canal = models.CharField(max_length=255, verbose_name="Medio o canal")
    # Links (al menos uno obligatorio, validado en clean())
    url_perfil_red = models.CharField(max_length=500, null=True, blank=True, verbose_name="URL perfil red social (Instagram, YouTube, TikTok, etc.)")
    url_sitio_medio = models.CharField(max_length=500, null=True, blank=True, verbose_name="URL sitio web del medio")
    seguidores_aprox = models.IntegerField(null=True, blank=True, verbose_name="Seguidores aproximados (solo influencers)")
    # Admin
    notas_admin = models.TextField(null=True, blank=True, verbose_name="Notas internas (solo admin)")
    acepta_tyc = models.BooleanField(default=False, verbose_name="Acepta Términos y Condiciones")
    fecha_inscripcion = models.DateTimeField(auto_now_add=True, db_index=True)

    def clean(self):
        """Al menos un link es obligatorio."""
        super().clean()
        if not self.url_perfil_red and not self.url_sitio_medio:
            raise ValidationError('Debe proporcionar al menos un link (perfil de red social o sitio web del medio).')

    def __str__(self):
        return f"{self.nombre_apellido} ({self.get_tipo_perfil_display()})"

    class Meta:
        ordering = ['-fecha_inscripcion']
        verbose_name = "Inscripción Prensa/Influencer"
        verbose_name_plural = "Inscripciones Prensa/Influencers"


class Inscripcion(models.Model):
    asistente = models.ForeignKey(Asistente, on_delete=models.CASCADE, related_name='inscripciones')
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, related_name='inscripciones')
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_inscripcion = models.DateTimeField(default=timezone.now)

    # --- Campos de Estado (Mapeados por edición) ---
    asistencia_confirmada = models.BooleanField(default=False, verbose_name="Asistencia Confirmada")
    fecha_confirmacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Confirmación")
    desea_alertas_laborales = models.BooleanField(default=False, verbose_name="¿Desea recibir alertas laborales?")
    history = HistoricalRecords()

    def __str__(self):
        return f"Inscripción de {self.asistente} - {self.edicion}"

    class Meta:
        unique_together = ('asistente', 'edicion')
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"

class Dashboard(models.Model):
    class Meta:
        managed = False
        verbose_name = "Dashboard de Estadísticas"
        verbose_name_plural = "📊 Dashboards de Estadísticas"
