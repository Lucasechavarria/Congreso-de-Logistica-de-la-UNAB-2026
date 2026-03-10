from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, Http404
from .models import Certificate

class CertificateDownloadView(APIView):
    def get(self, request, pk):
        try:
            cert = Certificate.objects.get(pk=pk)
        except Certificate.DoesNotExist:
            raise Http404("Certificado no encontrado")
        if not cert.pdf:
            cert.generate_pdf()
        if not cert.pdf:
            return Response({'error': 'No se pudo generar el PDF'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return FileResponse(cert.pdf.open('rb'), as_attachment=True, filename=cert.pdf.name.split('/')[-1])
