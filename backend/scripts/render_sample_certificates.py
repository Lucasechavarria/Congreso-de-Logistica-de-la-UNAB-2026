import os
import shutil
from PIL import Image, ImageDraw, ImageFont

def generate_samples():
    base_dir = r"c:\Users\User\Desktop\Congreso-UNAB-main\backend"
    cert_dir = os.path.join(base_dir, "certificates")
    font_path = os.path.join(base_dir, "api", "fonts", "DejaVu_Sans", "DejaVuSans-Bold.ttf")
    
    artifact_dir = r"C:\Users\User\.gemini\antigravity-ide\brain\da8ed597-f3a1-43fa-a35c-279ba7a6a2f1"
    os.makedirs(artifact_dir, exist_ok=True)
    
    # Also save to public/images for frontend if desired
    public_dir = r"c:\Users\User\Desktop\Congreso-UNAB-main\public\certificados_samples"
    os.makedirs(public_dir, exist_ok=True)

    samples = [
        {
            "type": "ASISTENCIA",
            "bg": "Certificados-congreso-2026.png",
            "name": "JUAN IGNACIO PÉREZ",
            "filename": "muestra_certificado_asistencia.png"
        },
        {
            "type": "DISERTANTE",
            "bg": "Certificados-congreso-disertantes-2026.png",
            "name": "DRA. MARIANA SÁNCHEZ",
            "filename": "muestra_certificado_disertante.png"
        },
        {
            "type": "EMPRESA",
            "bg": "Certificados-congreso-empresas-2026.png",
            "name": "LOGÍSTICA SUR TRANS S.A.",
            "filename": "muestra_certificado_empresa.png"
        }
    ]

    for item in samples:
        bg_file = os.path.join(cert_dir, item["bg"])
        if not os.path.exists(bg_file):
            print(f"File not found: {bg_file}")
            continue
            
        img = Image.open(bg_file).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        nombre_apellido = item["name"]
        
        # Scaling logic exactly as in models.py
        font_size = 65
        try:
            while font_size > 20:
                font = ImageFont.truetype(font_path, font_size)
                bbox = draw.textbbox((0, 0), nombre_apellido, font=font)
                text_width = bbox[2] - bbox[0]
                if text_width < 1500:
                    break
                font_size -= 5
        except Exception as e:
            print(f"Error loading font: {e}")
            font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), nombre_apellido, font=font)
            text_width = bbox[2] - bbox[0]

        x = (img.width - text_width) // 2
        y = 520
        
        draw.text((x, y), nombre_apellido, font=font, fill=(15, 41, 66))
        
        # Save full resolution in artifact and public dir
        target_art = os.path.join(artifact_dir, item["filename"])
        target_pub = os.path.join(public_dir, item["filename"])
        
        img.save(target_art, quality=95)
        img.save(target_pub, quality=95)
        print(f"Generated sample: {target_art}")

    # Also copy base templates to artifact dir
    for item in samples:
        bg_file = os.path.join(cert_dir, item["bg"])
        if os.path.exists(bg_file):
            shutil.copy(bg_file, os.path.join(artifact_dir, item["bg"]))

if __name__ == "__main__":
    generate_samples()
