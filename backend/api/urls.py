from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DisertanteViewSet, VerificarDNIView, ProgramaViewSet, RegistroEmpresasView, 
    RegistroViewSet, AsistenteCRMView, RegistroRapidoView, EmpresaViewSet, 
    CargaMasivaAsistentesView, EnvioMasivoEmailsView, ActualizarDNIView, 
    GetCSRFTokenView, RegistroDisertanteView, EmpresaCRMView, DisertanteCRMView,
    StatsDashboardView, InscripcionPrensaView, EdicionViewSet, BroadcastAPIView,
    DesuscripcionAlertasView
)
from .qr_views import GenerateStaticQRView

# Se crea un router para registrar los ViewSets
router = DefaultRouter()
router.register(r'disertantes', DisertanteViewSet, basename='disertante')
router.register(r'programa', ProgramaViewSet, basename='programa')
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'ediciones', EdicionViewSet, basename='edicion')

# Las URLs de la API son determinadas automáticamente por el router
urlpatterns = [
    path('', include(router.urls)),
    path('csrf/', GetCSRFTokenView.as_view(), name='get-csrf-token'),
    path('verificar-dni/', VerificarDNIView.as_view(), name='verificar-dni'),
    path('verificar-asistente/<str:dni>/', AsistenteCRMView.as_view(), name='verificar-asistente'),
    path('verificar-empresa/<str:email>/', EmpresaCRMView.as_view(), name='verificar-empresa'),
    path('verificar-disertante/<str:dni>/', DisertanteCRMView.as_view(), name='verificar-disertante'),
    path('generar-qrs/', GenerateStaticQRView.as_view(), name='generar-qrs'),
    path('registro/', RegistroViewSet.as_view({'post': 'create'}), name='registro-unificado'),
    path('stats/dashboard/', StatsDashboardView.as_view(), name='stats-dashboard'),
    path('registro-empresas/', RegistroEmpresasView.as_view({'post': 'create'}), name='registro-empresas'),
    path('inscripcion/', RegistroViewSet.as_view({'post': 'create'}), name='inscripcion-individual'),
    path('inscripcion-grupal/', RegistroViewSet.as_view({'post': 'create'}), name='inscripcion-grupal'),
    path('participantes/', RegistroViewSet.as_view({'post': 'create'}), name='participantes'),
    path('registro-rapido/', RegistroRapidoView.as_view({'post': 'create'}), name='registro-rapido'),
    path('carga-masiva/', CargaMasivaAsistentesView.as_view(), name='carga-masiva'),
    path('envio-masivo-emails/', EnvioMasivoEmailsView.as_view(), name='envio-masivo-emails'),
    path('actualizar-dni/', ActualizarDNIView.as_view(), name='actualizar-dni'),
    path('postulaciones-disertantes/', RegistroDisertanteView.as_view({'post': 'create'}), name='postulaciones-disertantes'),
    path('inscripcion-prensa/', InscripcionPrensaView.as_view(), name='inscripcion-prensa'),
    path('broadcast/', BroadcastAPIView.as_view(), name='broadcast-api'),
    path('desuscribir-alertas/', DesuscripcionAlertasView.as_view(), name='desuscribir-alertas'),
]