
# Script para generar certificados PDF para todos los disertantes de la base de datos
import os
import django
import sys
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Disertante

def generar_certificado_disertante(nombre_completo, email=None):
	base_path = os.path.join(BASE_DIR, 'certificates/Certificados-congreso-disertantes.png')
	nombre_upper = nombre_completo.upper()
	img = Image.open(base_path).convert("RGBA")
	draw = ImageDraw.Draw(img)
	font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
	font_size = 110
	try:
		font = ImageFont.truetype(font_path, font_size)
	except Exception:
		font = ImageFont.load_default()
	bbox = draw.textbbox((0, 0), nombre_upper, font=font)
	text_width = bbox[2] - bbox[0]
	x = (img.width - text_width) // 2
	y = 470
	draw.text((x, y), nombre_upper, font=font, fill=(18, 90, 150, 255))
	buffer = BytesIO()
	rgb_img = img.convert('RGB')
	rgb_img.save(buffer, format="PDF")
	buffer.seek(0)
	if email:
		safe_email = email.replace('@', '_').replace('.', '_')
		file_name = f"certificado_disertante_{safe_email}.pdf"
	else:
		safe_name = nombre_completo.replace(' ', '_').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n')
		file_name = f"certificado_disertante_{safe_name}.pdf"
	output_path = os.path.join(BASE_DIR, 'certificates', file_name)
	with open(output_path, 'wb') as f:
		f.write(buffer.getvalue())
	print(f"Certificado generado: {output_path}")

if __name__ == "__main__":
	disertantes = Disertante.objects.order_by('nombre')
	if not disertantes:
		print("No hay disertantes en la base de datos.")
		sys.exit(0)
	for disertante in disertantes:
		nombre = disertante.nombre
		email = None
		if hasattr(disertante, 'usuario') and disertante.usuario and disertante.usuario.email:
			email = disertante.usuario.email
		generar_certificado_disertante(nombre, email)
