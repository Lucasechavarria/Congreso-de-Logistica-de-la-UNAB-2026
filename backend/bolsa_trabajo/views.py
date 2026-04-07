from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django.utils import timezone
from django.db import models
from .models import OfertaLaboral
from .serializers import OfertaLaboralSerializer, OfertaLaboralCreateSerializer
from api.models import Empresa, Edicion

class OfertaLaboralCreateThrottle(AnonRateThrottle):
    rate = '5/hour'

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

class OfertaLaboralDetailView(generics.RetrieveAPIView):
    """
    Retorna el detalle completo de una oferta laboral por ID.
    Al ser detail, permitimos verla incluso si está PENDIENTE (para previsualización admin).
    """
    queryset = OfertaLaboral.objects.all()
    serializer_class = OfertaLaboralSerializer

class OfertaLaboralCreateView(generics.CreateAPIView):
    """
    Endpoint para que las empresas postulen nuevas vacantes.
    Implementa rate limiting y vinculación automática de empresa.
    """
    serializer_class = OfertaLaboralCreateSerializer
    throttle_classes = [OfertaLaboralCreateThrottle]

    def perform_create(self, serializer):
        # Campos de identificación de empresa (popeamos porque no son del modelo OfertaLaboral)
        nombre_empresa = serializer.validated_data.pop('nombre_empresa')
        cuit = serializer.validated_data.pop('cuit', None)
        email_contacto = serializer.validated_data.pop('email_contacto')

        # Buscar empresa existente por CUIT o Email
        empresa = None
        if cuit:
            empresa = Empresa.objects.filter(cuit=cuit).first()
        
        if not empresa:
            empresa = Empresa.objects.filter(email_contacto=email_contacto).first()

        # Si no existe, crear una nueva empresa en estado PENDIENTE
        if not empresa:
            edicion_activa = Edicion.objects.filter(activa=True).first()
            empresa = Empresa.objects.create(
                nombre_empresa=nombre_empresa,
                cuit=cuit,
                email_contacto=email_contacto,
                # email_empresa se asume igual al contacto si no se provee más info
                email_empresa=email_contacto,
                estado='PENDIENTE',
                edicion=edicion_activa
            )

        # Configurar campos automáticos de la oferta
        # Por defecto expira en 30 días
        fecha_expiracion = timezone.now() + timezone.timedelta(days=30)
        
        serializer.save(
            empresa=empresa,
            estado=OfertaLaboral.Estado.PENDIENTE,
            fecha_expiracion=fecha_expiracion
        )
