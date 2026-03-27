import os
from PIL import Image, ImageDraw, ImageFont

def generate_backgrounds():
    # Rutas
    base_dir = r"c:\Users\User\Desktop\Congreso-UNAB-main\backend"
    output_dir = os.path.join(base_dir, "certificates")
    os.makedirs(output_dir, exist_ok=True)

    # FONDO ELEGIDO: v20 - Rutas Logísticas Expandidas (2/3 de cobertura)
    selected_bg = r"C:\Users\User\.gemini\antigravity\brain\f9cf30f1-6618-42b5-b255-3adac0ec2b86\logistics_routes_full_v20_1_1774106025721.png"
    
    logo_negro_path = os.path.join(base_dir, "public", "images", "Logo_3.webp")
    signature_path = os.path.join(base_dir, "public", "images", "CONGRESO-LOGISTICA-2.png") 
    font_path = os.path.join(base_dir, "api", "fonts", "DejaVu_Sans", "DejaVuSans-Bold.ttf")

    # Dimensiones A4 Landscape a 300 DPI aprox (2000x1414)
    width, height = 2000, 1414

    # Extraer Firma
    try:
        sig_img = Image.open(signature_path).convert("RGBA")
        signature = sig_img.crop((34, 15, 663, 218))
    except:
        signature = None

    outputs = [
        (os.path.join(output_dir, f"Certificados-congreso-2026.png"), "asistente"),
        (os.path.join(output_dir, f"Certificados-congreso-disertantes-2026.png"), "disertante")
    ]

    for output_path, type_cert in outputs:
        # Cargar Fondo v20
        if os.path.exists(selected_bg):
            img = Image.open(selected_bg).convert("RGBA")
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            # Reducimos opacidad del overlay a 20 para MAXIMA VISIBILIDAD de las rutas
            overlay = Image.new('RGBA', (width, height), (255, 255, 255, 20)) 
            img = Image.alpha_composite(img, overlay)
        else:
            img = Image.new('RGBA', (width, height), (255, 255, 255, 255))
            
        draw = ImageDraw.Draw(img)

        # A. Logo Superior Central (550px)
        if os.path.exists(logo_negro_path):
            logo_top = Image.open(logo_negro_path).convert("RGBA")
            lw = 550
            aspect = logo_top.height / logo_top.width
            lh = int(lw * aspect)
            logo_top = logo_top.resize((lw, lh), Image.Resampling.LANCZOS)
            img.paste(logo_top, ((width - lw) // 2, 110), logo_top) 

        # B. JERARQUÍA COMPACTA (v13 compatible)
        try:
            main_font = ImageFont.truetype(font_path, 60)   
            body_font = ImageFont.truetype(font_path, 35)   
            date_font = ImageFont.truetype(font_path, 28)   
            rector_font = ImageFont.truetype(font_path, 26) 
        except:
            main_font = body_font = date_font = rector_font = ImageFont.load_default()

        # Texto base (Cuerpo elevado y=610 v13)
        text_part = "ha participado del" if type_cert == "asistente" else "ha participado como disertante del"
        tw = draw.textbbox((0, 0), text_part, font=body_font)[2]
        draw.text(((width - tw) // 2, 610), text_part, font=body_font, fill=(50, 50, 50, 255))

        # Congreso e Institución
        text_congreso = "CONGRESO DE LOGÍSTICA Y TRANSPORTE"
        tw = draw.textbbox((0, 0), text_congreso, font=main_font)[2]
        draw.text(((width - tw) // 2, 690), text_congreso, font=main_font, fill=(18, 90, 150, 255))

        text_uni = "en la UNIVERSIDAD NACIONAL GUILLERMO BROWN"
        tw = draw.textbbox((0, 0), text_uni, font=body_font)[2]
        draw.text(((width - tw) // 2, 770), text_uni, font=body_font, fill=(50, 50, 50, 255))

        text_date = "se extiende el presente certificado a los 7 días de Noviembre de 2026"
        tw = draw.textbbox((0, 0), text_date, font=date_font)[2]
        draw.text(((width - tw) // 2, 890), text_date, font=date_font, fill=(50, 50, 50, 255))

        # C. Firma
        if signature:
            sig_w = 500
            aspect = signature.height / signature.width
            sig_h = int(sig_w * aspect)
            sig_resized = signature.resize((sig_w, sig_h), Image.Resampling.LANCZOS)
            img.paste(sig_resized, ((width - sig_w) // 2, 960), sig_resized)

        # Rector
        text_rector = "Pablo Domenichini"
        text_cargo = "RECTOR UNAB"
        tw1 = draw.textbbox((0, 0), text_rector, font=rector_font)[2]
        tw2 = draw.textbbox((0, 0), text_cargo, font=rector_font)[2]
        draw.text(((width - tw1) // 2, 1090), text_rector, font=rector_font, fill=(0, 0, 0, 255))
        draw.text(((width - tw2) // 2, 1125), text_cargo, font=rector_font, fill=(0, 0, 0, 255))

        # D. Barra de Dominio Blue (v13 style)
        bar_height = 60
        draw.rectangle([0, height - bar_height, width, height], fill=(18, 90, 150, 255))
        web_text = "www.congresologistica.unab.edu.ar"
        tw_web = draw.textbbox((0, 0), web_text, font=rector_font)[2]
        draw.text(((width - tw_web) // 2, height - bar_height + 15), web_text, font=rector_font, fill=(255, 255, 255, 255))

        img.save(output_path)
        print(f"Finalizado v20 Enhanced Routes: {output_path}")

if __name__ == "__main__":
    generate_backgrounds()
