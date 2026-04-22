from rest_framework import serializers
from .models import (
    Edicion, Disertante, Programa, Empresa, Asistente, 
    Inscripcion, Certificado, PostulacionDisertante, InscripcionPrensa, MiembroGrupo
)
from django.db import transaction
from .email import send_group_confirmation_emails, send_individual_confirmation_email
import re


class EdicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edicion
        fields = ['id', 'anio', 'nombre', 'activa']


class InscripcionPrensaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InscripcionPrensa
        fields = '__all__'
        read_only_fields = ['edicion', 'fecha_inscripcion']

    def validate(self, data):
        url_red = data.get('url_perfil_red')
        url_medio = data.get('url_sitio_medio')
        if not url_red and not url_medio:
            raise serializers.ValidationError(
                'Debe proporcionar al menos un link (perfil de red social o sitio web del medio).'
            )
        return data


    def _upsert_detalles(self, asistente, data):
        """Helper para crear o actualizar los detalles específicos según el perfil"""
        from .models import DetalleEstudiante, DetalleDocente, DetalleProfesional, DetalleGrupo
        
        profile_type = asistente.profile_type
        if profile_type in [Asistente.ProfileType.STUDENT, Asistente.ProfileType.GRADUADO]:
            DetalleEstudiante.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'is_unab_student': data.get('is_unab_student') or False,
                    'institution': data.get('institution'),
                    'career': data.get('career'),
                    'year_of_study': data.get('year_of_study'),
                }
            )
        elif profile_type == Asistente.ProfileType.TEACHER:
            DetalleDocente.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'institution': data.get('institution'),
                    'career_taught': data.get('career_taught'),
                }
            )
        elif profile_type in [Asistente.ProfileType.PROFESSIONAL, Asistente.ProfileType.OTRO]:
            DetalleProfesional.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'work_area': data.get('work_area') if profile_type == Asistente.ProfileType.PROFESSIONAL else "Otro",
                    'occupation': data.get('occupation'),
                }
            )
        elif profile_type == Asistente.ProfileType.GROUP_REPRESENTATIVE:
            DetalleGrupo.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'group_name': data.get('group_name'),
                    'group_municipality': data.get('group_municipality'),
                    'group_size': data.get('group_size') or 0,
                }
            )

    def create(self, validated_data):
        from .models import Edicion
        edicion_activa = Edicion.objects.filter(activa=True).first()
        if not edicion_activa:
            raise serializers.ValidationError({'edicion': 'No hay una edición activa configurada en el sistema.'})
        
        email = validated_data.get('email')
        nombre = validated_data.get('nombre_apellido')
        
        # Upsert logic for Press
        inscripcion = InscripcionPrensa.objects.filter(email=email).first()
        if inscripcion:
            for attr, value in validated_data.items():
                setattr(inscripcion, attr, value)
            inscripcion.edicion = edicion_activa
            inscripcion.save()
        else:
            validated_data['edicion'] = edicion_activa
            inscripcion = InscripcionPrensa.objects.create(**validated_data)
            
        return inscripcion


class PostulacionDisertanteSerializer(serializers.ModelSerializer):
    ejes_tematicos = serializers.JSONField(required=False)
    publico_dirigido = serializers.JSONField(required=False)
    modalidad = serializers.JSONField(required=False)
    participacion_tipo = serializers.JSONField(required=False)

    def to_internal_value(self, data):
        import json
        ret = super().to_internal_value(data)
        for field in ['ejes_tematicos', 'publico_dirigido', 'modalidad', 'participacion_tipo']:
            if field in ret and not isinstance(ret[field], str):
                ret[field] = json.dumps(ret[field])
        return ret

    def to_representation(self, instance):
        import json
        ret = super().to_representation(instance)
        for field in ['ejes_tematicos', 'publico_dirigido', 'modalidad', 'participacion_tipo']:
            val = getattr(instance, field)
            if val and isinstance(val, str):
                try:
                    ret[field] = json.loads(val)
                except:
                    pass
        return ret

    def validate_linkedin(self, value):
        """Permite que linkedin sea opcional aceptando cadenas vacías o None."""
        if not value or (isinstance(value, str) and not value.strip()):
            return None
        return value

    class Meta:
        model = PostulacionDisertante
        fields = '__all__'
        read_only_fields = ['edicion', 'estado']


    def _upsert_detalles(self, asistente, data):
        """Helper para crear o actualizar los detalles específicos según el perfil"""
        from .models import DetalleEstudiante, DetalleDocente, DetalleProfesional, DetalleGrupo
        
        profile_type = asistente.profile_type
        if profile_type in [Asistente.ProfileType.STUDENT, Asistente.ProfileType.GRADUADO]:
            DetalleEstudiante.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'is_unab_student': data.get('is_unab_student') or False,
                    'institution': data.get('institution'),
                    'career': data.get('career'),
                    'year_of_study': data.get('year_of_study'),
                }
            )
        elif profile_type == Asistente.ProfileType.TEACHER:
            DetalleDocente.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'institution': data.get('institution'),
                    'career_taught': data.get('career_taught'),
                }
            )
        elif profile_type in [Asistente.ProfileType.PROFESSIONAL, Asistente.ProfileType.OTRO]:
            DetalleProfesional.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'work_area': data.get('work_area') if profile_type == Asistente.ProfileType.PROFESSIONAL else "Otro",
                    'occupation': data.get('occupation'),
                }
            )
        elif profile_type == Asistente.ProfileType.GROUP_REPRESENTATIVE:
            DetalleGrupo.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'group_name': data.get('group_name'),
                    'group_municipality': data.get('group_municipality'),
                    'group_size': data.get('group_size') or 0,
                }
            )

    def create(self, validated_data):
        from .models import Edicion
        edicion_activa = Edicion.objects.filter(activa=True).first()
        if not edicion_activa:
            raise serializers.ValidationError({"edicion": "No hay una edición activa configurada en el sistema."})

        dni = validated_data.get('dni')
        if not dni:
            raise serializers.ValidationError({"dni": "El DNI es obligatorio."})

        postulacion = PostulacionDisertante.objects.filter(dni=dni).first()
        if postulacion:
            # Update
            for attr, value in validated_data.items():
                setattr(postulacion, attr, value)
            postulacion.edicion = edicion_activa
            # Mantenemos o reseteamos a PENDIENTE, según req: 
            # Si se edita, quizas deberia volver a pendiente para ser reevaluada. 
            postulacion.estado = 'PENDIENTE' 
            postulacion.save()
        else:
            # Create
            validated_data['edicion'] = edicion_activa
            postulacion = PostulacionDisertante.objects.create(**validated_data)
        
        return postulacion

class DisertanteSerializer(serializers.ModelSerializer):
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Disertante
        fields = ['nombre', 'bio', 'foto_url', 'tema_presentacion', 'linkedin']

    def get_foto_url(self, obj):
        """
        Devuelve la URL absoluta de la foto del disertante.
        Garantiza que sea HTTPS para producción y HTTP para desarrollo local.
        """
        request = self.context.get('request', None)
        foto_url = ""
        
        # Obtener el origen (dominio + puerto)
        if request is not None:
            origin = request.build_absolute_uri('/')[:-1] # quita el / final
        else:
            # Fallback según DEBUG
            from django.conf import settings
            if settings.DEBUG:
                origin = "http://127.0.0.1:8000"
            else:
                origin = "https://www.congresologistica.unab.edu.ar"

        # Prioridad 1: Imagen subida al sistema (ImageField)
        if obj.foto:
            if request is not None:
                foto_url = request.build_absolute_uri(obj.foto.url)
            else:
                foto_url = f"{origin}{obj.foto.url}"
        
        # Prioridad 2: URL manual (CharField)
        elif obj.foto_url:
            foto_url = obj.foto_url.strip()
        
        # Si no hay foto, retornar vacío
        if not foto_url:
            return ""
        
        # Limpiar y normalizar la URL
        # Caso 1: Rutas absolutas mal formadas con path completo del servidor
        if "Congreso-UNAB/backend/media/" in foto_url:
            part = foto_url.split("media/")[-1]
            foto_url = f"{origin}/media/{part}"
        
        # Caso 2: Rutas relativas que empiezan con ponencias/ o media/
        elif foto_url.startswith("ponencias/"):
            foto_url = f"{origin}/media/{foto_url}"
        elif foto_url.startswith("media/"):
            foto_url = f"{origin}/{foto_url}"
        elif foto_url.startswith("/media/"):
            foto_url = f"{origin}{foto_url}"
        
        # Caso 3: Convertir a HTTPS solo si no es localhost/127.0.0.1
        if foto_url.startswith("http://"):
            if "localhost" not in foto_url and "127.0.0.1" not in foto_url:
                foto_url = foto_url.replace("http://", "https://")
        
        return foto_url

class ProgramaSerializer(serializers.ModelSerializer):
    disertantes = serializers.SerializerMethodField()

    class Meta:
        model = Programa
        fields = ['titulo', 'disertantes', 'hora_inicio', 'hora_fin', 'dia', 'descripcion', 'aula', 'categoria']
    
    def get_disertantes(self, obj):
        """Serializa los disertantes pasando el contexto de la request"""
        disertantes = obj.disertantes.all()
        serializer = DisertanteSerializer(disertantes, many=True, context=self.context)
        return serializer.data

class EmpresaSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        import json
        errors = {}
        # Solo nombre_empresa es estrictamente obligatorio aquí
        if not data.get('nombre_empresa'):
            errors['nombre_empresa'] = 'Este campo es obligatorio.'
        
        if errors:
            raise serializers.ValidationError(errors)
            
        ret = super().to_internal_value(data)
        
        # SQL_ASCII compatibility: stringify lists/dicts
        if 'participacion_opciones' in ret and not isinstance(ret['participacion_opciones'], str):
            ret['participacion_opciones'] = json.dumps(ret['participacion_opciones'])
            
        return ret

    def validate_sitio_web(self, value):
        """Permite que el sitio web sea opcional aceptando cadenas vacías o None."""
        if not value or (isinstance(value, str) and not value.strip()):
            return None
        return value

    def to_representation(self, instance):
        import json
        ret = super().to_representation(instance)
        # SQL_ASCII compatibility: parse JSON back to list/dict for frontend
        val = getattr(instance, 'participacion_opciones', None)
        if val and isinstance(val, str) and (val.startswith('[') or val.startswith('{')):
            try:
                ret['participacion_opciones'] = json.loads(val)
            except:
                pass
        return ret

    def validate_logo(self, value):
        """Validación flexible para el logo."""
        if not value:
            return None
        return value

    class Meta:
        model = Empresa
        fields = [
            'nombre_empresa',
            'cuit',
            'direccion',
            'telefono_empresa',
            'email_empresa',
            'sitio_web',
            'descripcion',
            'difusion_redes',
            'logo',
            'nombre_contacto',
            'email_contacto',
            'celular_contacto',
            'cargo_contacto',
            'participacion_opciones',
            'participacion_otra',
            'participo_edicion_anterior',
            'rubro_logistico',
            'requiere_electricidad',
            'computadora_o_pantalla',
            'tipo_mobiliario',
            'gazebo_propio',
            'estructura_adicional',
            'acciones_stand',
            'acepta_tyc',
            'edicion',
            'estado'
        ]
        read_only_fields = ['edicion', 'estado']


    def _upsert_detalles(self, asistente, data):
        """Helper para crear o actualizar los detalles específicos según el perfil"""
        from .models import DetalleEstudiante, DetalleDocente, DetalleProfesional, DetalleGrupo
        
        profile_type = asistente.profile_type
        if profile_type in [Asistente.ProfileType.STUDENT, Asistente.ProfileType.GRADUADO]:
            DetalleEstudiante.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'is_unab_student': data.get('is_unab_student') or False,
                    'institution': data.get('institution'),
                    'career': data.get('career'),
                    'year_of_study': data.get('year_of_study'),
                }
            )
        elif profile_type == Asistente.ProfileType.TEACHER:
            DetalleDocente.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'institution': data.get('institution'),
                    'career_taught': data.get('career_taught'),
                }
            )
        elif profile_type in [Asistente.ProfileType.PROFESSIONAL, Asistente.ProfileType.OTRO]:
            DetalleProfesional.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'work_area': data.get('work_area') if profile_type == Asistente.ProfileType.PROFESSIONAL else "Otro",
                    'occupation': data.get('occupation'),
                }
            )
        elif profile_type == Asistente.ProfileType.GROUP_REPRESENTATIVE:
            DetalleGrupo.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'group_name': data.get('group_name'),
                    'group_municipality': data.get('group_municipality'),
                    'group_size': data.get('group_size') or 0,
                }
            )

    def create(self, validated_data):
        from .models import Edicion
        edicion_activa = Edicion.objects.filter(activa=True).first()
        if not edicion_activa:
            raise serializers.ValidationError({"edicion": "No hay una edición activa configurada en el sistema."})

        # Si no hay email, verificamos si es una creación legítima de empresa
        email_empresa = validated_data.get('email_empresa')
        nombre_empresa = validated_data.get('nombre_empresa')
        
        if not email_empresa:
            if not nombre_empresa:
                # Caso de campo opcional vacío: devolvemos una instancia vacía o None manejado por el campo
                return None
            # Solo exigimos email si hay otros datos (como nombre_empresa)
            raise serializers.ValidationError({"email_empresa": "El email de la empresa es obligatorio para registro."})

        empresa = Empresa.objects.filter(email_empresa=email_empresa).first()
        if empresa:
            # Update 
            for attr, value in validated_data.items():
                setattr(empresa, attr, value)
            empresa.edicion = edicion_activa
            empresa.estado = 'PENDIENTE'
            empresa.save()
        else:
            # Create
            validated_data['edicion'] = edicion_activa
            empresa = Empresa.objects.create(**validated_data)
            
        return empresa


class EmpresaLogoSerializer(serializers.ModelSerializer):
    """
    Serializador simplificado para mostrar empresas en carrusel/slider.
    Solo incluye campos necesarios para mostrar logos.
    """
    class Meta:
        model = Empresa
        fields = ['id', 'nombre_empresa', 'logo', 'sitio_web', 'descripcion']

class MiembroGrupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiembroGrupo
        fields = ['full_name', 'dni']

class AsistenteGrupoSerializer(serializers.Serializer):
    """Serializer para miembros de grupo individuales"""
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    dni = serializers.CharField(max_length=8)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_type = serializers.CharField(required=False, default='VISITOR')
    institution = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    career = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    comision = serializers.CharField(required=False, allow_blank=True, allow_null=True)

class AsistenteSerializer(serializers.ModelSerializer):
    miembros_grupo = MiembroGrupoSerializer(many=True, required=False)  # Mantenemos compatibilidad
    miembros_grupo_nuevos = AsistenteGrupoSerializer(many=True, required=False, write_only=True)  # Nueva estructura
    miembros_representados = serializers.SerializerMethodField()  # Para lectura
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # Campos dinámicos para asistencia (según edición activa)
    asistencia_confirmada = serializers.SerializerMethodField()
    fecha_confirmacion = serializers.SerializerMethodField()
    
    # Overrides to disable UniqueValidator, as we do Upsert manually
    email = serializers.EmailField()
    dni = serializers.CharField(max_length=8, required=True, allow_blank=False)

    # Legacy fields now handled in related models, write_only to allow GET without AttributeError
    is_unab_student = serializers.BooleanField(required=False, allow_null=True, write_only=True)
    institution = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    career = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    year_of_study = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    career_taught = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    work_area = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    occupation = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    group_name = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    group_municipality = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    group_size = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    tipo_grupo = serializers.JSONField(required=False, write_only=True)
    comision = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Asistente
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'dni', 'profile_type',
            'is_unab_student', 'institution', 'career', 'year_of_study',
            'career_taught', 'work_area', 'occupation',
            'group_name', 'group_municipality', 'group_size', 'tipo_grupo',
            'miembros_grupo', 'miembros_grupo_nuevos', 'miembros_representados', 'rol_especifico',
            'comision',
            'prensa_medio', 'prensa_links', 'asistencia_confirmada', 'fecha_confirmacion'
        ]
        read_only_fields = ['id', 'miembros_representados']
        extra_kwargs = {
            'is_unab_student': {'required': False},
            'institution': {'required': False},
            'career': {'required': False},
            'year_of_study': {'required': False},
            'career_taught': {'required': False},
            'work_area': {'required': False},
            'occupation': {'required': False},
            'group_name': {'required': False},
            'group_municipality': {'required': False},
            'group_size': {'required': False},
            'comision': {'required': False},
        }

    def to_internal_value(self, data):
        import json
        ret = super().to_internal_value(data)
        for field in ['tipo_grupo', 'prensa_links']:
            if field in ret and ret[field] is not None and not isinstance(ret[field], str):
                ret[field] = json.dumps(ret[field])
        return ret

    def to_representation(self, instance):
        import json
        ret = super().to_representation(instance)
        # SQL_ASCII compatibility: parse JSON back to list/dict for frontend
        for field in ['tipo_grupo', 'prensa_links']:
            val = getattr(instance, field, None)
            if val and isinstance(val, str) and (val.startswith('[') or val.startswith('{')):
                try:
                    ret[field] = json.loads(val)
                except:
                    pass
        # Handle tipo_grupo if it belongs to DetalleGrupo
        if hasattr(instance, 'detalle_grupo'):
            val = instance.detalle_grupo.tipo_grupo
            if val and isinstance(val, str) and (val.startswith('[') or val.startswith('{')):
                try:
                    ret['tipo_grupo'] = json.loads(val)
                except:
                    pass
        
        # Pull data from detail models if they exist
        profile_type = instance.profile_type
        
        if profile_type in [Asistente.ProfileType.STUDENT, Asistente.ProfileType.GRADUADO] and hasattr(instance, 'detalle_estudiante'):
            detalle = instance.detalle_estudiante
            ret['is_unab_student'] = getattr(detalle, 'is_unab_student', False)
            ret['institution'] = detalle.institution
            ret['career'] = detalle.career
            ret['year_of_study'] = detalle.year_of_study
            
        elif profile_type == Asistente.ProfileType.TEACHER and hasattr(instance, 'detalle_docente'):
            detalle = instance.detalle_docente
            ret['institution'] = detalle.institution
            ret['career_taught'] = detalle.career_taught
            
        elif profile_type in [Asistente.ProfileType.PROFESSIONAL, Asistente.ProfileType.OTRO] and hasattr(instance, 'detalle_profesional'):
            detalle = instance.detalle_profesional
            ret['work_area'] = detalle.work_area
            ret['occupation'] = detalle.occupation
            
        elif profile_type == Asistente.ProfileType.GROUP_REPRESENTATIVE and hasattr(instance, 'detalle_grupo'):
            ret['group_name'] = detalle.group_name
            ret['group_municipality'] = detalle.group_municipality
        
        # Pull base fields
        ret['comision'] = instance.comision
        return ret

    def get_miembros_representados(self, obj):
        """Devuelve la información de los miembros representados"""
        if obj.es_representante_grupo:
            miembros = obj.get_miembros_grupo()
            return [{
                'id': m.id,
                'first_name': m.first_name,
                'last_name': m.last_name,
                'email': m.email,
                'dni': m.dni
            } for m in miembros]
        return []

    def get_asistencia_confirmada(self, obj):
        edicion_activa = Edicion.objects.filter(activa=True).first()
        if not edicion_activa: return False
        insc = obj.inscripciones.filter(edicion=edicion_activa).first()
        return insc.asistencia_confirmada if insc else False

    def get_fecha_confirmacion(self, obj):
        edicion_activa = Edicion.objects.filter(activa=True).first()
        if not edicion_activa: return None
        insc = obj.inscripciones.filter(edicion=edicion_activa).first()
        return insc.fecha_confirmacion if insc else None


    def _upsert_detalles(self, asistente, data):
        """Helper para crear o actualizar los detalles específicos según el perfil"""
        from .models import DetalleEstudiante, DetalleDocente, DetalleProfesional, DetalleGrupo
        
        profile_type = asistente.profile_type
        if profile_type in [Asistente.ProfileType.STUDENT, Asistente.ProfileType.GRADUADO]:
            DetalleEstudiante.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'is_unab_student': data.get('is_unab_student') or False,
                    'institution': data.get('institution'),
                    'career': data.get('career'),
                    'year_of_study': data.get('year_of_study'),
                }
            )
        elif profile_type == Asistente.ProfileType.TEACHER:
            DetalleDocente.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'institution': data.get('institution'),
                    'career_taught': data.get('career_taught'),
                }
            )
        elif profile_type in [Asistente.ProfileType.PROFESSIONAL, Asistente.ProfileType.OTRO]:
            DetalleProfesional.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'work_area': data.get('work_area') if profile_type == Asistente.ProfileType.PROFESSIONAL else "Otro",
                    'occupation': data.get('occupation'),
                }
            )
        elif profile_type == Asistente.ProfileType.GROUP_REPRESENTATIVE:
            DetalleGrupo.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'group_name': data.get('group_name'),
                    'group_municipality': data.get('group_municipality'),
                    'group_size': data.get('group_size') or 0,
                }
            )

    def create(self, validated_data):
        from .models import DetalleEstudiante, DetalleDocente, DetalleProfesional, DetalleGrupo
        from django.db import transaction

        miembros_data = validated_data.pop('miembros_grupo', [])  # Compatibilidad con sistema anterior
        miembros_nuevos_data = validated_data.pop('miembros_grupo_nuevos', [])  # Nuevo sistema
        
        # Extraer campos de Detalle
        is_unab_student = validated_data.pop('is_unab_student', False)
        institution = validated_data.pop('institution', None)
        career = validated_data.pop('career', None)
        year_of_study = validated_data.pop('year_of_study', None)
        career_taught = validated_data.pop('career_taught', None)
        work_area = validated_data.pop('work_area', None)
        occupation = validated_data.pop('occupation', None)
        group_name = validated_data.pop('group_name', None)
        group_municipality = validated_data.pop('group_municipality', None)
        group_size = validated_data.pop('group_size', 0)
        tipo_grupo = validated_data.get('tipo_grupo')

        dni = validated_data.get('dni')
        email = validated_data.get('email')

        # 1. Registro del REPRESENTANTE (Atomico para el individuo)
        edicion_activa = Edicion.objects.filter(activa=True).first()
        try:
            with transaction.atomic():
                asistente = None
                if dni:
                    asistente = Asistente.objects.filter(dni=dni).first()
                if not asistente and email:
                    asistente = Asistente.objects.filter(email=email).first()

                if asistente:
                    for attr, value in validated_data.items():
                        setattr(asistente, attr, value)
                    asistente.save()
                else:
                    asistente = Asistente.objects.create(**validated_data)

                # Detalles del representante
                self._upsert_detalles(asistente, {
                    'is_unab_student': is_unab_student,
                    'institution': institution,
                    'career': career,
                    'year_of_study': year_of_study,
                    'career_taught': career_taught,
                    'work_area': work_area,
                    'occupation': occupation,
                    'group_name': group_name,
                    'group_municipality': group_municipality,
                    'group_size': group_size
                })

        except Exception as e:
            # Si falla el representante, no tiene sentido seguir con el grupo
            raise serializers.ValidationError({"detail": f"Error al registrar representante: {str(e)}"})

        # Para que el serializer pueda mostrar los valores, los asignamos dinámicamente
        asistente.is_unab_student = is_unab_student
        asistente.institution = institution
        asistente.career = career
        asistente.year_of_study = year_of_study
        asistente.career_taught = career_taught
        asistente.work_area = work_area
        asistente.occupation = occupation
        asistente.group_name = group_name
        asistente.group_municipality = group_municipality
        asistente.group_size = group_size
        
        if asistente.profile_type == Asistente.ProfileType.GROUP_REPRESENTATIVE:
            # 2. Registro de MIEMBROS (Independientes entre sí)
            
            # Sistema anterior - mantenemos compatibilidad
            for miembro_data in miembros_data:
                try:
                    with transaction.atomic():
                        MiembroGrupo.objects.get_or_create(representante=asistente, dni=miembro_data.get('dni'), defaults=miembro_data)
                except:
                    pass # Silencioso para compatibilidad heredada
            
            # Nuevo sistema - crear/actualizar asistentes individuales
            fallos_miembros = []
            for miembro_data in miembros_nuevos_data:
                try:
                    with transaction.atomic():
                        m_dni = miembro_data.get('dni')
                        m_email = miembro_data.get('email')
                        
                        if not m_dni and not m_email:
                            raise ValueError("Nombre, Email o DNI faltantes en integrante.")

                        m_asistente = None
                        if m_dni:
                            m_asistente = Asistente.objects.filter(dni=m_dni).first()
                        if not m_asistente and m_email:
                            m_asistente = Asistente.objects.filter(email=m_email).first()
                        
                        m_profile = miembro_data.get('profile_type', Asistente.ProfileType.VISITOR)
                        m_defaults = {
                            'first_name': miembro_data['first_name'],
                            'last_name': miembro_data['last_name'],
                            'email': m_email,
                            'dni': m_dni,
                            'phone': miembro_data.get('phone'),
                            'profile_type': m_profile,
                            'representante_grupo': asistente,
                            'comision': miembro_data.get('comision') or validated_data.get('comision'),
                            'terminos_aceptados': True,
                        }

                        if m_asistente:
                            for attr, value in m_defaults.items():
                                setattr(m_asistente, attr, value)
                            m_asistente.save()
                        else:
                            m_asistente = Asistente.objects.create(**m_defaults)
                        
                        # Guardar detalles del integrante si aplica
                        self._upsert_detalles(m_asistente, {
                            'institution': miembro_data.get('institution'),
                            'career': miembro_data.get('career'),
                        })

                        # Vincular miembro a Edición Activa
                        if edicion_activa:
                            Inscripcion.objects.get_or_create(asistente=m_asistente, edicion=edicion_activa)

                except Exception as e:
                    fallos_miembros.append(f"{miembro_data.get('first_name', 'Fila')} - {str(e)}")

            if fallos_miembros:
                print(f"[WARNING] Errores en integrantes de grupo: {fallos_miembros}")
            
            # Enviar emails de confirmación
            try:
                resultado_envio = send_group_confirmation_emails(asistente)
                asistente._email_enviado = (resultado_envio['total_fallidos'] == 0)
            except Exception as e:
                asistente._email_enviado = False
                print(f"[ERROR] Error enviando emails grupales: {e}")
        else:
            # Para inscripciones individuales
            try:
                asistente._email_enviado = send_individual_confirmation_email(asistente)
            except Exception as e:
                asistente._email_enviado = False
                print(f"[ERROR] Error enviando email individual: {e}")
        
        return asistente

    def validate_dni(self, value):
        """Valida que el DNI tenga exactamente 8 dígitos numéricos"""
        if value:
            # Limpiar caracteres no numéricos
            dni_limpio = re.sub(r'\D', '', value)
            # Si tiene 9 dígitos y termina en 0, eliminar el último 0
            if len(dni_limpio) == 9 and dni_limpio.endswith('0'):
                # Usar slice explícito para evitar confusiones del linter
                dni_limpio = dni_limpio[:8]
            # Validar que tenga exactamente 8 dígitos
            if len(dni_limpio) != 8 or not dni_limpio.isdigit():
                raise serializers.ValidationError('El DNI debe tener exactamente 8 dígitos numéricos.')
            return dni_limpio
        return value

    def validate(self, data):
        profile_type = data.get('profile_type')

        if profile_type == Asistente.ProfileType.STUDENT:
            if data.get('is_unab_student') is None:
                raise serializers.ValidationError({"is_unab_student": "Este campo es requerido para estudiantes."})
            if data.get('is_unab_student') is False and not data.get('institution'):
                raise serializers.ValidationError({"institution": "La institución es requerida si no perteneces a la UNaB."})
            if not data.get('career'):
                raise serializers.ValidationError({"career": "La carrera es requerida para estudiantes."})
            if not data.get('year_of_study'):
                raise serializers.ValidationError({"year_of_study": "El año de cursada es requerido para estudiantes."})

        elif profile_type == Asistente.ProfileType.TEACHER:
            if not data.get('institution'):
                raise serializers.ValidationError({"institution": "La institución es requerida para docentes."})
            if not data.get('career_taught'):
                raise serializers.ValidationError({"career_taught": "La carrera que dicta es requerida para docentes."})

        elif profile_type == Asistente.ProfileType.PROFESSIONAL:
            if not data.get('work_area'):
                raise serializers.ValidationError({"work_area": "El área de trabajo es requerida para profesionales."})
            if not data.get('occupation'):
                raise serializers.ValidationError({"occupation": "El cargo es requerido para profesionales."})

        elif profile_type == Asistente.ProfileType.PRESS:
            # No hay campos obligatorios extra para prensa
            pass
        elif profile_type == 'GROUP_REPRESENTATIVE':
            if data.get('group_name') is None: # Solo error si es totalmente nulo/ausente
                raise serializers.ValidationError({"group_name": "El nombre del grupo o institución es requerido."})
            if data.get('group_size') is None:
                raise serializers.ValidationError({"group_size": "La cantidad de personas es requerida."})
            
            # Validar que tenga miembros (sistema anterior o nuevo)
            miembros_antiguos = data.get('miembros_grupo', [])
            miembros_nuevos = data.get('miembros_grupo_nuevos', [])
            
            if not miembros_antiguos and not miembros_nuevos:
                raise serializers.ValidationError({
                    "miembros_grupo": "Debe proporcionar la lista de miembros del grupo."
                })
            
        return data

class InscripcionSerializer(serializers.ModelSerializer):
    asistente = AsistenteSerializer() # Nested AsistenteSerializer

    class Meta:
        model = Inscripcion
        fields = ['asistente', 'empresa', 'fecha_inscripcion', 'edicion', 'desea_alertas_laborales'] 
        read_only_fields = ['fecha_inscripcion', 'edicion']


    def _upsert_detalles(self, asistente, data):
        """Helper para crear o actualizar los detalles específicos según el perfil"""
        from .models import DetalleEstudiante, DetalleDocente, DetalleProfesional, DetalleGrupo
        
        profile_type = asistente.profile_type
        if profile_type in [Asistente.ProfileType.STUDENT, Asistente.ProfileType.GRADUADO]:
            DetalleEstudiante.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'is_unab_student': data.get('is_unab_student') or False,
                    'institution': data.get('institution'),
                    'career': data.get('career'),
                    'year_of_study': data.get('year_of_study'),
                }
            )
        elif profile_type == Asistente.ProfileType.TEACHER:
            DetalleDocente.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'institution': data.get('institution'),
                    'career_taught': data.get('career_taught'),
                }
            )
        elif profile_type in [Asistente.ProfileType.PROFESSIONAL, Asistente.ProfileType.OTRO]:
            DetalleProfesional.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'work_area': data.get('work_area') if profile_type == Asistente.ProfileType.PROFESSIONAL else "Otro",
                    'occupation': data.get('occupation'),
                }
            )
        elif profile_type == Asistente.ProfileType.GROUP_REPRESENTATIVE:
            DetalleGrupo.objects.update_or_create(
                asistente=asistente,
                defaults={
                    'group_name': data.get('group_name'),
                    'group_municipality': data.get('group_municipality'),
                    'group_size': data.get('group_size') or 0,
                }
            )

    def create(self, validated_data):
        from .models import Edicion
        asistente_data = validated_data.pop('asistente')
        
        # Delegamos completamente la creación/upsert del asistente a AsistenteSerializer
        asistente_serializer = AsistenteSerializer(data=asistente_data)
        asistente_serializer.is_valid(raise_exception=True)
        asistente = asistente_serializer.save()

        edicion = Edicion.objects.filter(activa=True).first()
        if not edicion:
            raise serializers.ValidationError({"edicion": "No hay una edición activa disponible."})

        # Prevenir duplicidad de inscripción a la misma edición
        if Inscripcion.objects.filter(asistente=asistente, edicion=edicion).exists():
            raise serializers.ValidationError({"detail": f"Ya te encuentras registrado/a en la edición {edicion.nombre}."})

        inscripcion = Inscripcion.objects.create(asistente=asistente, edicion=edicion, **validated_data)
        return inscripcion
