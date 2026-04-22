from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('django.skills')

class PremiumAPIView(APIView):
    """
    Skill: Premium Django API Base
    Proporciona un estándar de respuesta, logging automático y manejo de errores global.
    """
    def handle_exception(self, exc):
        logger.error(f"[API Skill] Exception in {self.__class__.__name__}: {str(exc)}", exc_info=True)
        return Response({
            "status": "error",
            "message": "Ocurrió un error interno en el servidor.",
            "detail": str(exc) if True else None # Cambiar True por settings.DEBUG
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def success_response(self, data=None, message="Operación exitosa", status_code=status.HTTP_200_OK):
        return Response({
            "status": "success",
            "message": message,
            "data": data
        }, status=status.HTTP_200_OK)

    def error_response(self, message="Error en la solicitud", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            "status": "error",
            "message": message,
            "errors": errors
        }, status=status_code)
