from django.urls import path
from .views import OfertaLaboralListView, OfertaLaboralCreateView

urlpatterns = [
    path('ofertas/', OfertaLaboralListView.as_view(), name='oferta-laboral-list'),
    path('ofertas/nueva/', OfertaLaboralCreateView.as_view(), name='oferta-laboral-create'),
]
