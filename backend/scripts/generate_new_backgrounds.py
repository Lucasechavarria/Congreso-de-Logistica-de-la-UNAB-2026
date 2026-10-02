import os
import math
from PIL import Image, ImageDraw, ImageFont

def generate_backgrounds():
    # Base paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, ".."))
    root_dir = os.path.abspath(os.path.join(base_dir, ".."))
    
    output_dir = os.path.join(base_dir, "certificates")
    os.makedirs(output_dir, exist_ok=True)

    # Assets
    logo_unab_path = os.path.join(root_dir, "public", "images", "LogoUnab_Cyan.png")
    cg2_path = os.path.join(root_dir, "public", "images", "CONGRESO-LOGISTICA-2.png")
    font_path = os.path.join(base_dir, "api", "fonts", "DejaVu_Sans", "DejaVuSans-Bold.ttf")
    logo_cin_path = os.path.join(root_dir, "public", "images", "logo_cin.png")
    sig_path = os.path.join(root_dir, "public", "images", "Firma_Rector_Transparent.png")

    # Dimensions: High Resolution A4 Landscape (2000x1414)
    width, height = 2000, 1414

    # Load Images
    try:
        logo_unab_img = Image.open(logo_unab_path).convert("RGBA")
    except Exception as e:
        print(f"[WARN] No se pudo cargar LogoUnab.png: {e}")
        logo_unab_img = None

    try:
        logo_cin_img = Image.open(logo_cin_path).convert("RGBA")
    except Exception as e:
        print(f"[WARN] No se pudo cargar logo_cin.png: {e}")
        logo_cin_img = None

    try:
        logo_cg2_img = Image.open(cg2_path).convert("RGBA")
        cg2_bbox = logo_cg2_img.getbbox()
        if cg2_bbox:
            logo_cg2_img = logo_cg2_img.crop(cg2_bbox)
    except Exception as e:
        print(f"[WARN] No se pudo cargar CONGRESO-LOGISTICA-2.png: {e}")
        logo_cg2_img = None

    try:
        sig_img = Image.open(sig_path).convert("RGBA")
        sig_bbox = sig_img.getbbox()
        if sig_bbox:
            sig_img = sig_img.crop(sig_bbox)
    except Exception as e:
        print(f"[WARN] No se pudo cargar Firma_Rector_Transparent.png: {e}")
        sig_img = None

    # Certificate Types configuration
    certs = [
        (
            "Certificados-congreso-2026.png",
            "ASISTENCIA",
            "CERTIFICADO DE ASISTENCIA",
            "por su participación en el",
            "2º CONGRESO DE LOGÍSTICA Y TRANSPORTE"
        ),
        (
            "Certificados-congreso-disertantes-2026.png",
            "DISERTANTE",
            "CERTIFICADO DE DISERTANTE",
            "en reconocimiento a su valiosa disertación en el",
            "2º CONGRESO DE LOGÍSTICA Y TRANSPORTE"
        ),
        (
            "Certificados-congreso-empresas-2026.png",
            "EMPRESA",
            "CERTIFICADO DE RECONOCIMIENTO EMPRESARIAL",
            "en agradecimiento por su apoyo e integración institucional en el",
            "2º CONGRESO DE LOGÍSTICA Y TRANSPORTE"
        )
    ]

    for filename, cert_type, title, body1, body2 in certs:
        # 1. Base Pristine Canvas (Soft Ivory Off-White)
        img = Image.new('RGBA', (width, height), (252, 252, 254, 255))
        draw = ImageDraw.Draw(img)

        # 2. Layer for Translucent Vector Art & Security Micro-Lattice (Guilloché)
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        d_overlay = ImageDraw.Draw(overlay)

        # Background Security Guilloché Mesh (Diamond pattern)
        grid_step = 60
        for x in range(-height, width + height, grid_step):
            d_overlay.line([x, 0, x + height, height], fill=(210, 220, 235, 22), width=1)
            d_overlay.line([x, height, x + height, 0], fill=(210, 220, 235, 22), width=1)

        # Corner Luxury Radial Waves (Navy & Gold tones)
        d_overlay.ellipse([-600, -500, 900, 1000], fill=(15, 41, 66, 18))
        d_overlay.ellipse([-500, -400, 750, 850], fill=(0, 168, 204, 25))
        d_overlay.ellipse([-400, -300, 600, 700], fill=(197, 160, 89, 20))

        d_overlay.ellipse([width - 900, height - 1000, width + 600, height + 500], fill=(15, 41, 66, 18))
        d_overlay.ellipse([width - 750, height - 850, width + 500, height + 400], fill=(0, 168, 204, 25))
        d_overlay.ellipse([width - 600, height - 700, width + 400, height + 300], fill=(197, 160, 89, 20))

        # Composite background overlay
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

        # 3. Triple Frame System (Luxury Outer Dark Navy, Double Gold Inset, Cyan Hairline)
        # Outer Navy Frame
        margin_outer = 35
        draw.rectangle([margin_outer, margin_outer, width - margin_outer, height - margin_outer], outline=(15, 41, 66, 255), width=8)

        # Gold Main Frame
        margin_gold = 48
        draw.rectangle([margin_gold, margin_gold, width - margin_gold, height - margin_gold], outline=(197, 160, 89, 255), width=4)

        # Gold Inner Parallel Hairline
        margin_gold_inner = 55
        draw.rectangle([margin_gold_inner, margin_gold_inner, width - margin_gold_inner, height - margin_gold_inner], outline=(212, 175, 55, 255), width=1)

        # Cyan Subtle Accent Frame
        margin_cyan = 62
        draw.rectangle([margin_cyan, margin_cyan, width - margin_cyan, height - margin_cyan], outline=(0, 168, 204, 180), width=2)

        # Corner Filigree Accents (Ornamental L-Shapes in all 4 corners)
        corner_len = 50
        for cx, cy in [(margin_gold_inner, margin_gold_inner), 
                       (width - margin_gold_inner, margin_gold_inner), 
                       (margin_gold_inner, height - margin_gold_inner), 
                       (width - margin_gold_inner, height - margin_gold_inner)]:
            dx = 1 if cx < width / 2 else -1
            dy = 1 if cy < height / 2 else -1
            # Corner L-line
            draw.line([cx, cy, cx + (corner_len * dx), cy], fill=(197, 160, 89, 255), width=4)
            draw.line([cx, cy, cx, cy + (corner_len * dy)], fill=(197, 160, 89, 255), width=4)
            # Corner Diamond Dot
            diam_size = 6
            draw.polygon([
                (cx + (15 * dx), cy + (15 * dy) - diam_size),
                (cx + (15 * dx) + diam_size, cy + (15 * dy)),
                (cx + (15 * dx), cy + (15 * dy) + diam_size),
                (cx + (15 * dx) - diam_size, cy + (15 * dy))
            ], fill=(197, 160, 89, 255))

        # 4. Header Section: Logos & Top Institutional Identity (Increased top margin)
        if logo_unab_img:
            u_h = 105
            u_w = int(logo_unab_img.width * (u_h / logo_unab_img.height))
            unab_resized = logo_unab_img.resize((u_w, u_h), Image.Resampling.LANCZOS)
            img.paste(unab_resized, (110, 110), unab_resized)

        if logo_cin_img:
            cin_h = 80
            cin_w = int(logo_cin_img.width * (cin_h / logo_cin_img.height))
            cin_resized = logo_cin_img.resize((cin_w, cin_h), Image.Resampling.LANCZOS)
            img.paste(cin_resized, (width - 110 - cin_w, 122), cin_resized)

        if logo_cg2_img:
            c_h = 115
            c_w = int(logo_cg2_img.width * (c_h / logo_cg2_img.height))
            if c_w > 500:
                c_w = 500
                c_h = int(logo_cg2_img.height * (c_w / logo_cg2_img.width))
            congreso_resized = logo_cg2_img.resize((c_w, c_h), Image.Resampling.LANCZOS)
            img.paste(congreso_resized, ((width - c_w) // 2, 100), congreso_resized)

        # Fonts Setup
        try:
            f_inst = ImageFont.truetype(font_path, 20)
            f_title = ImageFont.truetype(font_path, 50)
            f_subtitle = ImageFont.truetype(font_path, 28)
            f_body = ImageFont.truetype(font_path, 30)
            f_body_highlight = ImageFont.truetype(font_path, 34)
            f_date = ImageFont.truetype(font_path, 24)
            f_rector_name = ImageFont.truetype(font_path, 26)
            f_rector_title = ImageFont.truetype(font_path, 20)
            f_footer = ImageFont.truetype(font_path, 20)
        except Exception:
            f_inst = f_title = f_subtitle = f_body = f_body_highlight = f_date = f_rector_name = f_rector_title = f_footer = ImageFont.load_default()

        # Top Center Institution Line
        inst_text = "UNIVERSIDAD NACIONAL GUILLERMO BROWN"
        inst_bbox = draw.textbbox((0, 0), inst_text, font=f_inst)
        inst_w = inst_bbox[2] - inst_bbox[0]
        draw.text(((width - inst_w) // 2, 245), inst_text, font=f_inst, fill=(15, 41, 66, 255))

        # Decorative Divider Line with Center Golden Diamond
        draw.line([650, 275, 1350, 275], fill=(197, 160, 89, 255), width=2)
        draw.polygon([(1000, 271), (1005, 275), (1000, 279), (995, 275)], fill=(197, 160, 89, 255))

        # 5. Certificate Title
        t_bbox = draw.textbbox((0, 0), title, font=f_title)
        t_w = t_bbox[2] - t_bbox[0]
        draw.text(((width - t_w) // 2, 315), title, font=f_title, fill=(15, 41, 66, 255))

        # 6. Subtitle / Intro
        intro = 'Se otorga el presente certificado a' if cert_type != 'EMPRESA' else 'Se otorga el presente certificado a la empresa'
        sub_bbox = draw.textbbox((0, 0), intro, font=f_subtitle)
        sub_w = sub_bbox[2] - sub_bbox[0]
        draw.text(((width - sub_w) // 2, 405), intro, font=f_subtitle, fill=(71, 85, 105, 255))

        # 7. Name Slot Accent Line (Underline for the participant name rendered by models.py at y = 485)
        # Elegant Golden & Navy dual underline with central diamond at y = 565
        draw.line([300, 565, 1700, 565], fill=(197, 160, 89, 255), width=2)
        draw.line([500, 568, 1500, 568], fill=(15, 41, 66, 180), width=1)
        draw.polygon([(1000, 561), (1007, 565), (1000, 569), (993, 565)], fill=(197, 160, 89, 255))

        # 8. Institutional Body Text
        b1_bbox = draw.textbbox((0, 0), body1, font=f_body)
        b1_w = b1_bbox[2] - b1_bbox[0]
        draw.text(((width - b1_w) // 2, 615), body1, font=f_body, fill=(51, 65, 85, 255))

        b2_bbox = draw.textbbox((0, 0), body2, font=f_body_highlight)
        b2_w = b2_bbox[2] - b2_bbox[0]
        draw.text(((width - b2_w) // 2, 670), body2, font=f_body_highlight, fill=(15, 41, 66, 255))

        org_line = 'organizado por la Universidad Nacional Guillermo Brown'
        org_bbox = draw.textbbox((0, 0), org_line, font=f_body)
        org_w = org_bbox[2] - org_bbox[0]
        draw.text(((width - org_w) // 2, 725), org_line, font=f_body, fill=(51, 65, 85, 255))

        # Location & Date Line
        date_line = 'Burzaco, Almirante Brown, 7 de Noviembre de 2026'
        d_bbox = draw.textbbox((0, 0), date_line, font=f_date)
        d_w = d_bbox[2] - d_bbox[0]
        draw.text(((width - d_w) // 2, 790), date_line, font=f_date, fill=(100, 116, 139, 255))

        # 9. Signature Section (Bottom-Center - Tightened bottom spacing)
        if sig_img:
            s_w = 320
            s_h = int(sig_img.height * (s_w / sig_img.width))
            sig_resized = sig_img.resize((s_w, s_h), Image.Resampling.LANCZOS)
            img.paste(sig_resized, ((width - s_w) // 2, 970), sig_resized)

        # Signature Separator Line & Gold Accents
        draw.line([700, 1150, 1300, 1150], fill=(15, 41, 66, 255), width=2)
        draw.polygon([(1000, 1147), (1005, 1150), (1000, 1153), (995, 1150)], fill=(197, 160, 89, 255))

        r_name = 'Lic. Pablo Domenichini'
        rn_bbox = draw.textbbox((0, 0), r_name, font=f_rector_name)
        rn_w = rn_bbox[2] - rn_bbox[0]
        draw.text(((width - rn_w) // 2, 1165), r_name, font=f_rector_name, fill=(15, 41, 66, 255))

        r_title = 'Rector — Universidad Nacional Guillermo Brown'
        rt_bbox = draw.textbbox((0, 0), r_title, font=f_rector_title)
        rt_w = rt_bbox[2] - rt_bbox[0]
        draw.text(((width - rt_w) // 2, 1205), r_title, font=f_rector_title, fill=(100, 116, 139, 255))

        # 10. Institutional Bottom Footer Bar (Navy & Gold Bar)
        bar_h = 60
        draw.rectangle([0, height - bar_h, width, height], fill=(15, 41, 66, 255))
        draw.line([0, height - bar_h, width, height - bar_h], fill=(197, 160, 89, 255), width=3)

        footer_text = 'UNIVERSIDAD NACIONAL GUILLERMO BROWN  •  CONGRESO DE LOGÍSTICA Y TRANSPORTE 2026'
        ft_bbox = draw.textbbox((0, 0), footer_text, font=f_footer)
        ft_w = ft_bbox[2] - ft_bbox[0]
        draw.text(((width - ft_w) // 2, height - bar_h + 18), footer_text, font=f_footer, fill=(255, 255, 255, 255))

        out_path = os.path.join(output_dir, filename)
        img.save(out_path)
        print(f"[OK] Certificado {cert_type} generado exitosamente en: {out_path}")

if __name__ == "__main__":
    generate_backgrounds()



