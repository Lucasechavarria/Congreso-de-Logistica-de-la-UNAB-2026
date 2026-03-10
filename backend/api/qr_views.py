import qrcode
from io import BytesIO
import base64
from django.http import JsonResponse
from django.views import View
from django.conf import settings
import os
from PIL import Image, ImageDraw, ImageFont

class GenerateStaticQRView(View):
    """
    Vista para generar QRs estáticos:
    1. QR para confirmar asistencia (redirige a verificación de DNI)
    2. QR para inscripción in-situ (redirige a registro rápido)
    """
    
    def get(self, request):
        # URLs base del frontend (producción)
        frontend_base = "https://www.congresologistica.unab.edu.ar"

        # URLs para los QRs estáticos
        checkin_url = f"{frontend_base}/verificar-dni"
        registro_url = f"{frontend_base}/registro-rapido"

        # Generar QR para check-in
        checkin_qr = qrcode.QRCode(
            version=2,  # Un poco más grande para mejor contraste
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Mejor tolerancia al logo
            box_size=12,
            border=4
        )
        checkin_qr.add_data(checkin_url)
        checkin_qr.make(fit=True)
        checkin_img = checkin_qr.make_image(fill_color="black", back_color="white").convert('RGBA')

        # Rutas de los logos
        unab_logo_path = os.path.join(settings.BASE_DIR, 'media', 'unab-logo.png')
        folkode_logo_path = os.path.join(settings.BASE_DIR, 'media', 'folkode-logo-oscuro.webp')
        
        print(f"DEBUG: Buscando logo UNAB en: {unab_logo_path}")
        print(f"DEBUG: Buscando logo FolKode en: {folkode_logo_path}")
        print(f"DEBUG: UNAB existe: {os.path.exists(unab_logo_path)}")
        print(f"DEBUG: FolKode existe: {os.path.exists(folkode_logo_path)}")
        
        # Insertar logo de UNAB en el centro del QR
        if os.path.exists(unab_logo_path):
            unab_logo = Image.open(unab_logo_path).convert('RGBA')
            qr_width, qr_height = checkin_img.size
            
            # Mantener la proporción original del logo UNAB
            original_width, original_height = unab_logo.size
            # Hacer que el logo ocupe ~45% del ancho del QR (mucho más grande)
            logo_width = int(qr_width * 0.45)
            logo_height = int((logo_width * original_height) / original_width)
            
            unab_logo = unab_logo.resize((logo_width, logo_height), Image.LANCZOS)
            
            # Crear fondo blanco rectangular con padding mínimo
            padding = 8
            bg_width = logo_width + (padding * 2)
            bg_height = logo_height + (padding * 2)
            
            logo_bg = Image.new('RGBA', (bg_width, bg_height), (255, 255, 255, 255))
            
            # Pegar el logo en el centro del fondo blanco
            logo_pos = (padding, padding)
            logo_bg.paste(unab_logo, logo_pos, unab_logo)
            
            # Pegar el logo con fondo en el centro del QR
            center_pos = ((qr_width - bg_width) // 2, (qr_height - bg_height) // 2)
            checkin_img.paste(logo_bg, center_pos, logo_bg)
        
        # Agregar logos de FolKode en las cuatro esquinas del QR
        if os.path.exists(folkode_logo_path):
            folkode_logo = Image.open(folkode_logo_path).convert('RGBA')
            corner_size = 50
            
            # Redimensionar el logo de FolKode
            logo_corner_size = corner_size - 16
            folkode_resized = folkode_logo.resize((logo_corner_size, logo_corner_size), Image.LANCZOS)
            
            # Crear fondo blanco cuadrado para cada esquina
            corner_bg = Image.new('RGBA', (corner_size, corner_size), (255, 255, 255, 255))
            corner_draw = ImageDraw.Draw(corner_bg)
            corner_draw.rectangle([0, 0, corner_size-1, corner_size-1], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
            
            # Pegar el logo de FolKode en el centro del cuadrado
            logo_pos = ((corner_size - logo_corner_size) // 2, (corner_size - logo_corner_size) // 2)
            corner_bg.paste(folkode_resized, logo_pos, folkode_resized)
            
            # Posiciones de las tres esquinas (evitamos inferior derecha)
            corners = [
                (8, 8),  # Superior izquierda
                (qr_width - corner_size - 8, 8),  # Superior derecha
                (8, qr_height - corner_size - 8),  # Inferior izquierda
            ]
            
            for pos in corners:
                checkin_img.paste(corner_bg, pos, corner_bg)
        
        if not os.path.exists(unab_logo_path):
            print(f"ADVERTENCIA: No se encontró el logo UNAB en {unab_logo_path}")
        if not os.path.exists(folkode_logo_path):
            print(f"ADVERTENCIA: No se encontró el logo FolKode en {folkode_logo_path}")

        # Generar QR para registro (sin logo)
        registro_qr = qrcode.QRCode(version=1, box_size=10, border=5)
        registro_qr.add_data(registro_url)
        registro_qr.make(fit=True)
        registro_img = registro_qr.make_image(fill_color="black", back_color="white")

        # Convertir a base64 para enviar como respuesta
        checkin_buffer = BytesIO()
        checkin_img.save(checkin_buffer, format='PNG')
        checkin_b64 = base64.b64encode(checkin_buffer.getvalue()).decode()

        registro_buffer = BytesIO()
        registro_img.save(registro_buffer, format='PNG')
        registro_b64 = base64.b64encode(registro_buffer.getvalue()).decode()

        return JsonResponse({
            'checkin_qr': {
                'url': checkin_url,
                'image_base64': f"data:image/png;base64,{checkin_b64}",
                'description': 'QR para confirmar asistencia (verificación de DNI)'
            },
            'registro_qr': {
                'url': registro_url, 
                'image_base64': f"data:image/png;base64,{registro_b64}",
                'description': 'QR para inscripción in-situ en el evento'
            }
        })
