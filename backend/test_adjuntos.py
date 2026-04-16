import os
import django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

# Configurar Django para el script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.email import get_tyc_path, attach_tyc

def test_attachment():
    print("--- Probando Diagnóstico de Adjuntos ---")
    
    # 1. Verificar tipos
    tipos = ['asistente', 'empresa', 'disertante']
    
    for tipo in tipos:
        path = get_tyc_path(tipo)
        exists = os.path.exists(path)
        print(f"Tipo: {tipo}")
        print(f" - Ruta esperada: {path}")
        print(f" - ¿Existe en disco?: {'SÍ' if exists else 'NO'}")
        
        if exists:
            # Intentar crear un objeto email y adjuntar
            email = EmailMultiAlternatives("Test", "Body", "from@test.com", ["to@test.com"])
            success = attach_tyc(email, tipo)
            print(f" - Intento de adjunto: {'EXITOSO' if success else 'FALLIDO'}")
        print("-" * 30)

if __name__ == "__main__":
    test_attachment()
