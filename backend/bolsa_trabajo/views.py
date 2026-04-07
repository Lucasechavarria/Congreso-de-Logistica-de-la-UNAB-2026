from rest_framework import generics
from django.utils import timezone
from .models import OfertaLaboral
from .serializers import OfertaLaboralSerializer

class OfertaLaboralListView(generics.ListAPIView):
    serializer_class = OfertaLaboralSerializer
    
    def get_queryset(self):
        """
        Retorna solo las ofertas aprobadas que no han expirado.
        """
        now = timezone.now()
        return OfertaLaboral.objects.filter(
            estado=OfertaLaboral.Estado.APROBADO,
            fecha_expiracion__gt=now
        )
