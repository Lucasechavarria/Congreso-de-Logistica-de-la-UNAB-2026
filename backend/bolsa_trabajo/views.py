from rest_framework import generics
from django.utils import timezone
from django.db import models
from .models import OfertaLaboral
from .serializers import OfertaLaboralSerializer

class OfertaLaboralListView(generics.ListAPIView):
    serializer_class = OfertaLaboralSerializer
    
    def get_queryset(self):
        """
        Retorna solo las ofertas aprobadas que no han expirado,
        aplicando filtros opcionales de búsqueda, modalidad y empresa.
        """
        now = timezone.now()
        queryset = OfertaLaboral.objects.filter(
            estado=OfertaLaboral.Estado.APROBADO,
            fecha_expiracion__gt=now
        )

        # Filtro de búsqueda (q) - Título o descripción
        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(
                models.Q(titulo_puesto__icontains=q) | 
                models.Q(descripcion__icontains=q)
            )

        # Filtro de modalidad
        modalidad = self.request.query_params.get('modalidad')
        if modalidad:
            queryset = queryset.filter(modalidad=modalidad)

        # Filtro de empresa (ID)
        empresa_id = self.request.query_params.get('empresa')
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)

        return queryset
