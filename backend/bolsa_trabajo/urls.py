from django.urls import path
from .views import (
    OfertaLaboralListView, OfertaLaboralCreateView, 
    OfertaLaboralDetailView, PostulacionOfertaCreateView
)

urlpatterns = [
    path('ofertas/', OfertaLaboralListView.as_view(), name='oferta-laboral-list'),
    path('ofertas/nueva/', OfertaLaboralCreateView.as_view(), name='oferta-laboral-create'),
    path('ofertas/<int:pk>/', OfertaLaboralDetailView.as_view(), name='oferta-laboral-detail'),
    path('ofertas/postular/', PostulacionOfertaCreateView.as_view(), name='postulacion-oferta-create'),
]
