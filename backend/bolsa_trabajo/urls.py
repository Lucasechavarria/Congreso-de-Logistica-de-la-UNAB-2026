from django.urls import path
from .views import OfertaLaboralListView

urlpatterns = [
    path('ofertas/', OfertaLaboralListView.as_view(), name='oferta-laboral-list'),
]
