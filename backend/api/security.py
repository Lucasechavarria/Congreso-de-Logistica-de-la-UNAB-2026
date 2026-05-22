from functools import wraps
import html
import logging
from rest_framework.throttling import SimpleRateThrottle

logger = logging.getLogger('django.security')

def sanitize_value(val):
    """
    Función recursiva y liviana para escapar etiquetas HTML
    y sanitizar entradas contra inyecciones XSS de forma nativa.
    """
    if isinstance(val, str):
        # Escapado nativo y liviano de caracteres HTML peligrosos
        cleaned = html.escape(val.strip())
        # Remover protocolos de script directos para evitar XSS en href
        cleaned = cleaned.replace("javascript:", "")
        cleaned = cleaned.replace("data:", "")
        return cleaned
    elif isinstance(val, dict):
        return {k: sanitize_value(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [sanitize_value(i) for i in val]
    return val

def sanitize_xss_payload(view_func):
    """
    Decorador para métodos de vistas (post, put, patch) en Django REST Framework
    que sanea automáticamente el payload de entrada en 'request.data' antes
    de que sea procesado o serializado.
    """
    @wraps(view_func)
    def wrapped(self, request, *args, **kwargs):
        if hasattr(request, 'data') and request.data:
            try:
                # Almacenar copia original opcional por trazabilidad interna
                request._original_data = request.data
                # Reemplazar la data de la solicitud con la data saneada
                request._data = sanitize_value(request.data)
            except Exception as e:
                logger.error(f"[XSS Sanitizer] Error al sanear payload en {self.__class__.__name__}: {str(e)}")
        return view_func(self, request, *args, **kwargs)
    return wrapped


class DNIVerificationThrottle(SimpleRateThrottle):
    """
    Límite de tasa específico para verificar DNI (evita scraping de asistentes).
    Por defecto se configura a 10 peticiones por minuto.
    """
    scope = 'dni_verification'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class FormRegistrationThrottle(SimpleRateThrottle):
    """
    Límite de tasa específico para los formularios de registro (empresa, disertante, participantes).
    Por defecto se configura a 5 peticiones por minuto.
    """
    scope = 'form_registration'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
