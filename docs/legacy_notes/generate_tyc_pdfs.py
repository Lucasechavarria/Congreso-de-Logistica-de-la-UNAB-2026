import os
import django
from django.conf import settings
from django.template.loader import render_to_string
from xhtml2pdf import pisa

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def generate_all_tyc_pdfs():
    static_dir = os.path.join(settings.MEDIA_ROOT, 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    files = [
        ('api/pdf/tyc_disertantes.html', 'Bases_Disertantes_2026.pdf'),
        ('api/pdf/tyc_empresas.html', 'Bases_Empresas_2026.pdf'),
        ('api/pdf/tyc_asistentes.html', 'Bases_Asistentes_2026.pdf'),
    ]
    
    logo_path = os.path.join(settings.BASE_DIR, 'media', 'logo-final-negro.png')
    
    for template, output_name in files:
        html = render_to_string(template, {'logo_path': logo_path})
        pdf_path = os.path.join(static_dir, output_name)
        with open(pdf_path, 'wb') as f:
            pisa.CreatePDF(html, dest=f)
        print(f'PDF creado: {pdf_path}')

if __name__ == "__main__":
    generate_all_tyc_pdfs()
