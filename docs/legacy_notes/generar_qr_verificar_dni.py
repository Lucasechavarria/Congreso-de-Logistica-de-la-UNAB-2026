import qrcode
import os

# URL de la vista de verificación de asistencia
url = "https://www.congresologistica.unab.edu.ar/verificar-dni"

# Carpeta destino
output_dir = os.path.join(os.path.dirname(__file__), "qr_codes")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "qr_verificar_dni.png")

# Generar el QR
qr = qrcode.QRCode(
    version=2,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=12,
    border=4
)
qr.add_data(url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")

# Guardar el archivo
img.save(output_path)
print(f"QR guardado en: {output_path}")