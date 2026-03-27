import os
from PIL import Image, ImageDraw, ImageFont

def combine_previews():
    base_dir = r"c:\Users\User\Desktop\Congreso-UNAB-main\backend"
    cert_dir = os.path.join(base_dir, "certificates")
    output_path = r"C:\Users\User\.gemini\antigravity\brain\f9cf30f1-6618-42b5-b255-3adac0ec2b86\COMPARATIVA_FINAL_LOGISTICA.png"
    
    files = [
        "Certificados-congreso-L1.png",
        "Certificados-congreso-L2.png",
        "Certificados-congreso-L3.png"
    ]
    
    images = []
    for f in files:
        path = os.path.join(cert_dir, f)
        if os.path.exists(path):
            images.append(Image.open(path))
            
    if not images:
        print("No se encontraron imagenes")
        return

    # Redimensionar para que quepan (600px ancho cada una)
    target_w = 600
    resized_imgs = []
    for img in images:
        aspect = img.height / img.width
        resized_imgs.append(img.resize((target_w, int(target_w * aspect)), Image.Resampling.LANCZOS))
        
    # Crear lienzo
    total_w = target_w * 3 + 40 # Margenes
    total_h = resized_imgs[0].height + 100
    canvas = Image.new('RGB', (total_w, total_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    
    # Fuentes para etiquetas
    try:
        font_path = os.path.join(base_dir, "api", "fonts", "DejaVu_Sans", "DejaVuSans-Bold.ttf")
        font = ImageFont.truetype(font_path, 40)
    except:
        font = ImageFont.load_default()
        
    labels = ["L1: RED GLOBAL", "L2: FLUJO DINAMICO", "L3: CONECTIVIDAD"]
    
    for i, img in enumerate(resized_imgs):
        x = 10 + i * (target_w + 10)
        canvas.paste(img, (x, 10))
        draw.text((x + 50, total_h - 70), labels[i], font=font, fill=(0, 0, 0))
        
    canvas.save(output_path)
    print(f"Comparativa guardada en: {output_path}")

if __name__ == "__main__":
    combine_previews()
