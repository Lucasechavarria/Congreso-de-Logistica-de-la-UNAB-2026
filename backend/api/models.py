from django.db import models
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
    linkedin = models.URLField(blank=True, null=True, verbose_name="Perfil de LinkedIn")
    tema_presentacion = models.CharField(max_length=255, verbose_name="Título de la Presentación")

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']

class PostulacionDisertante(models.Model):
    edicion = models.ForeignKey('Edicion', on_delete=models.CASCADE, null=True, blank=True, related_name='postulaciones_disertantes')
    # Personal & Profesional
    nombre_apellido = models.CharField(max_length=200, verbose_name="Nombre y Apellido")
    dni = models.CharField(max_length=8, verbose_name="DNI / Documento")
    email = models.EmailField(verbose_name="Email de contacto")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    ciudad_provincia = models.CharField(max_length=255, verbose_name="Ciudad y Provincia")
    profesion_cargo = models.CharField(max_length=255, verbose_name="Profesión / Cargo actual")
    empresa_institucion = models.CharField(max_length=255, verbose_name="Empresa / Institución a la que pertenece")
    linkedin = models.URLField(blank=True, null=True, verbose_name="LinkedIn u otra red profesional")
    
    # Propuesta de Charla
    titulo_charla = models.CharField(max_length=255, verbose_name="Título de la exposición")
    ejes_tematicos = models.JSONField(default=list, blank=True, verbose_name="Eje temático al que se vincula (Array de strings)")
    eje_otro = models.TextField(blank=True, null=True, verbose_name="Otro eje temático")
    resumen_charla = models.TextField(verbose_name="Resumen de la charla (máx. 300 palabras)")
    objetivos_charla = models.TextField(verbose_name="Objetivos de la exposición")
    publico_dirigido = models.JSONField(default=list, verbose_name="Público al que está dirigida (Array de strings)")
    
    # Modalidad y Participación
    modalidad = models.JSONField(default=list, verbose_name="Formato preferido (Array de strings)")
    participacion_tipo = models.JSONField(default=list, verbose_name="Tipo de participación (Array de strings)")
    
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
    fecha_postulacion = models.DateTimeField(auto_now_add=True)

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
    ESTADO_CHOICES = [('PENDIENTE', 'Pendiente'), ('APROBADO', 'Aprobado'), ('RECHAZADO', 'Rechazado')]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado")
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Fecha de registro")
    # Main Info
    nombre_empresa = models.CharField(max_length=255, verbose_name="Nombre de la empresa o institución")
    cuit = models.CharField(max_length=15, blank=True, null=True, verbose_name="CUIT de la empresa")
    direccion = models.CharField(max_length=500, blank=True, null=True, verbose_name="Dirección de la empresa")
    telefono_empresa = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono de la empresa")
    email_empresa = models.EmailField(blank=True, null=True, verbose_name="Email corporativo de la empresa")
    sitio_web = models.URLField(blank=True, null=True, verbose_name="Sitio web de la empresa")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción de la empresa")
    logo = models.FileField(upload_to='logos_empresas/', blank=True, null=True, verbose_name="Logo de la empresa")

    # Contact Person
    nombre_contacto = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nombre completo de la persona de contacto")
    email_contacto = models.EmailField(unique=False, blank=True, null=True, verbose_name="Correo electrónico de la persona de contacto")
    celular_contacto = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número de celular de contacto")
    cargo_contacto = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cargo que cumple en la empresa / institución")

    # Participation
    participacion_opciones = models.CharField(max_length=50, blank=True, null=True, verbose_name="¿Cómo les gustaría participar?")
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
        PRESS = 'PRESS', 'Prensa'
        GROUP_REPRESENTATIVE = 'GROUP_REPRESENTATIVE', 'Representante de Grupo'
        GRADUADO = 'GRADUADO', 'Graduado'
        OTRO = 'OTRO', 'Otro'

    # --- Información Principal (Común a todos) ---
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número de celular")
    dni = models.CharField(max_length=8, unique=True, null=True, blank=True, verbose_name="DNI")
    dni_update_token = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name="Token de actualización de DNI")
    dni_email_sent = models.BooleanField(default=False, verbose_name="Email de solicitud DNI enviado")
    dni_email_sent_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha envío email DNI")
    profile_type = models.CharField(max_length=30, choices=ProfileType.choices, verbose_name="Tipo de Perfil")
    
    # Campo adicional para roles específicos (ej: "Colaborador/a Estudiante", "Colaborador/a Docente")
    rol_especifico = models.CharField(max_length=255, blank=True, null=True, verbose_name="Rol Específico")

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

    # --- Información adicional ---
    ciudad_provincia = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ciudad / Provincia")
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Fecha de registro")

    # --- Campos de Estado para QR y Certificados ---
    asistencia_confirmada = models.BooleanField(default=False, verbose_name="Asistencia Confirmada")
    fecha_confirmacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Confirmación")

    # --- Términos y Condiciones ---
    terminos_aceptados = models.BooleanField(default=False, verbose_name="Acepta Términos y Condiciones")

    def __str__(self):
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
            # Validar que tenga entre 7 y 8 dígitos
            if not (7 <= len(dni_limpio) <= 8) or not dni_limpio.isdigit():
                raise ValidationError({
                    'dni': 'El DNI debe tener entre 7 y 8 dígitos numéricos.'
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

    def __str__(self):
        return f"{self.full_name} (Grupo de {self.representante})"

class Certificado(models.Model):
    class TipoCertificado(models.TextChoices):
        ASISTENCIA = 'ASISTENCIA', 'Asistencia'
        DISERTANTE = 'DISERTANTE', 'Disertante'
        EMPRESA = 'EMPRESA', 'Empresa'

    asistente = models.ForeignKey(Asistente, on_delete=models.CASCADE)
    tipo_certificado = models.CharField(max_length=10, choices=TipoCertificado.choices, verbose_name="Tipo de Certificado")
    pdf_generado = models.FileField(upload_to='certificados/', storage=storages["private"], blank=True, null=True, verbose_name="PDF Generado")
    fecha_generacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Generación")

    def __str__(self):
        return f"Certificado de {self.get_tipo_certificado_display()} para {self.asistente.first_name} {self.asistente.last_name}" # type: ignore

    def generar_pdf(self, save=True): # type: ignore
        """
        Genera un PDF personalizado usando la imagen base y superponiendo el nombre del asistente.
        """
        import os
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO

        # --- SOLUCIÓN: Usar BASE_DIR de Django para construir rutas absolutas y seguras ---
        from django.conf import settings
        from django.core.files.base import ContentFile
        base_path = os.path.join(settings.BASE_DIR, 'certificates', 'Certificados-congreso.png')

        # Escribir el nombre en mayúsculas para reemplazar el texto de la plantilla
        nombre_apellido = f"{self.asistente.first_name} {self.asistente.last_name}".upper()

        # Abrir la imagen base
        img = Image.open(base_path).convert("RGB") # Convertir a RGB para guardar en PDF
        draw = ImageDraw.Draw(img)
        
        # --- SOLUCIÓN: No depender de fuentes del sistema. Incluir la fuente en el proyecto. ---
        # Coloca el archivo .ttf en una carpeta dentro de tu app, por ejemplo: 'api/fonts/'
        font_path = os.path.join(settings.BASE_DIR, 'api', 'fonts', 'DejaVu_Sans', 'DejaVuSans-Bold.ttf')
        
        # Ajustar tamaño de fuente y posición para que reemplace exactamente 'NOMBRE Y APELLIDO'
        font_size = 110  # Puedes ajustar este valor si el texto no encaja perfecto
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception:
            font = ImageFont.load_default()

        # --- MEJORA: Usar textbbox para un centrado más preciso ---
        try:
            # Método moderno para medir texto
            bbox = draw.textbbox((0, 0), nombre_apellido, font=font)
            text_width = bbox[2] - bbox[0]
        except AttributeError:
            # Fallback para versiones antiguas de Pillow
            text_width, _ = draw.textsize(nombre_apellido, font=font)  # type: ignore

        x = (img.width - text_width) / 2
        y = 470  # Ajusta este valor vertical si es necesario
        # Escribir el texto (color azul similar al diseño)
        draw.text((x, y), nombre_apellido, font=font, fill=(18, 90, 150, 255))

        # Convertir la imagen a PDF en memoria
        buffer = BytesIO()
        img.save(buffer, format="PDF", resolution=100.0)
        buffer.seek(0)
        file_name = f"certificado_{self.asistente.email}.pdf"
        self.pdf_generado.save(file_name, ContentFile(buffer.getvalue()), save=save)

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
    tipo_grupo = models.JSONField(default=list, verbose_name="Tipo de grupo", help_text="Opciones: ESCOLAR, UNIVERSITARIO, INSTITUCIONAL, EMPRESARIAL, OTRO")

class InscripcionPrensa(models.Model):
    """Registro voluntario de prensa e influencers. Sin convocatoria formal."""
    edicion = models.ForeignKey('Edicion', on_delete=models.CASCADE, null=True, blank=True, related_name='inscripciones_prensa')
    # Identidad
    nombre_apellido = models.CharField(max_length=200, verbose_name="Nombre y Apellido")
    dni = models.CharField(max_length=8, verbose_name="DNI")
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
    url_perfil_red = models.URLField(null=True, blank=True, verbose_name="URL perfil red social (Instagram, YouTube, TikTok, etc.)")
    url_sitio_medio = models.URLField(null=True, blank=True, verbose_name="URL sitio web del medio")
    seguidores_aprox = models.IntegerField(null=True, blank=True, verbose_name="Seguidores aproximados (solo influencers)")
    # Admin
    notas_admin = models.TextField(null=True, blank=True, verbose_name="Notas internas (solo admin)")
    acepta_tyc = models.BooleanField(default=False, verbose_name="Acepta Términos y Condiciones")
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

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

    class Meta:
        unique_together = ('asistente', 'edicion')

    def __str__(self):
        return f"Inscripción de {self.asistente} - {self.edicion}"

class Dashboard(models.Model):
    class Meta:
        managed = False
        verbose_name = "Dashboard de Estadísticas"
        verbose_name_plural = "📊 Dashboards de Estadísticas"
