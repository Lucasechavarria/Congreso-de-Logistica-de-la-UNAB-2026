from rest_framework import serializers
from .models import OfertaLaboral
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
