from rest_framework import serializers
from .models import OfertaLaboral, PostulacionOferta
from api.serializers import EmpresaSerializer

class OfertaLaboralSerializer(serializers.ModelSerializer):
    empresa_detalle = EmpresaSerializer(source='empresa', read_only=True)
    
    class Meta:
        model = OfertaLaboral
        fields = [
            'id', 'empresa', 'empresa_detalle', 'titulo_puesto', 'descripcion', 
            'requisitos', 'modalidad', 'ubicacion', 'canal_postulacion', 
            'estado', 'fecha_creacion', 'fecha_expiracion'
        ]

class OfertaLaboralCreateSerializer(serializers.ModelSerializer):
    # Campos adicionales para identificar/crear la empresa
    nombre_empresa = serializers.CharField(write_only=True)
    cuit = serializers.CharField(write_only=True, required=False, allow_null=True)
    email_contacto = serializers.EmailField(write_only=True)

    class Meta:
        model = OfertaLaboral
        fields = [
            'nombre_empresa', 'cuit', 'email_contacto',
            'titulo_puesto', 'descripcion', 'requisitos', 
            'modalidad', 'ubicacion', 'canal_postulacion'
        ]

    def validate_modalidad(self, value):
        if value not in dict(OfertaLaboral.Modalidad.choices):
            raise serializers.ValidationError("Modalidad no válida.")
        return value

class PostulacionOfertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostulacionOferta
        fields = '__all__'
