import os
from PIL import Image, ImageDraw, ImageFont

def generate_balanced_certificates():
    base_dir = r"c:\Users\User\Desktop\Congreso-UNAB-main\backend"
    root_dir = os.path.abspath(os.path.join(base_dir, ".."))
    cert_dir = os.path.join(base_dir, "certificates")
    font_path = os.path.join(base_dir, "api", "fonts", "DejaVu_Sans", "DejaVuSans-Bold.ttf")
    
    artifact_dir = r"C:\Users\User\.gemini\antigravity-ide\brain\da8ed597-f3a1-43fa-a35c-279ba7a6a2f1"
    os.makedirs(artifact_dir, exist_ok=True)
    
    public_dir = r"c:\Users\User\Desktop\Congreso-UNAB-main\public\certificados_samples"
    os.makedirs(public_dir, exist_ok=True)

    # Assets
    logo_unab_path = os.path.join(root_dir, "public", "images", "LogoUnab_Cyan.png")
    cg2_path = os.path.join(root_dir, "public", "images", "logo-congreso-2026-negro.png")
    logo_cin_path = os.path.join(root_dir, "public", "images", "logo_cin.png")
    sig_path = os.path.join(root_dir, "public", "images", "Firma_Rector_Transparent.png")

    width, height = 2000, 1414

    # Load Assets
    l_unab = Image.open(logo_unab_path).convert("RGBA") if os.path.exists(logo_unab_path) else None
    l_cin = Image.open(logo_cin_path).convert("RGBA") if os.path.exists(logo_cin_path) else None
    l_cg2 = Image.open(cg2_path).convert("RGBA") if os.path.exists(cg2_path) else None
    sig_img = Image.open(sig_path).convert("RGBA") if os.path.exists(sig_path) else None

    if l_cg2:
        bbox = l_cg2.getbbox()
        if bbox:
            l_cg2 = l_cg2.crop(bbox)

    if sig_img:
        sbbox = sig_img.getbbox()
        if sbbox:
            sig_img = sig_img.crop(sbbox)

    # Fonts
    f_inst = ImageFont.truetype(font_path, 21)
    f_title = ImageFont.truetype(font_path, 48)
    f_subtitle = ImageFont.truetype(font_path, 27)
    f_body = ImageFont.truetype(font_path, 29)
    f_body_highlight = ImageFont.truetype(font_path, 33)
    f_date = ImageFont.truetype(font_path, 24)
    f_rector_name = ImageFont.truetype(font_path, 26)
    f_rector_title = ImageFont.truetype(font_path, 20)
    f_footer = ImageFont.truetype(font_path, 20)

    certs = [
        {
            "filename": "Certificados-congreso-2026.png",
            "sample_file": "muestra_certificado_asistencia.png",
            "type": "ASISTENCIA",
            "title": "CERTIFICADO DE ASISTENCIA",
            "intro": "Se otorga el presente certificado a",
            "sample_name": "JUAN IGNACIO PÉREZ",
            "body1": "por su participación en el",
            "body2": "2º CONGRESO DE LOGÍSTICA Y TRANSPORTE"
        },
        {
            "filename": "Certificados-congreso-disertantes-2026.png",
            "sample_file": "muestra_certificado_disertante.png",
            "type": "DISERTANTE",
            "title": "CERTIFICADO DE DISERTANTE",
            "intro": "Se otorga el presente certificado a",
            "sample_name": "DRA. MARIANA SÁNCHEZ",
            "body1": "en reconocimiento a su valiosa disertación en el",
            "body2": "2º CONGRESO DE LOGÍSTICA Y TRANSPORTE"
        },
        {
            "filename": "Certificados-congreso-empresas-2026.png",
            "sample_file": "muestra_certificado_empresa.png",
            "type": "EMPRESA",
            "title": "CERTIFICADO DE RECONOCIMIENTO EMPRESARIAL",
            "intro": "Se otorga el presente certificado a la empresa",
            "sample_name": "LOGÍSTICA SUR TRANS S.A.",
            "body1": "en agradecimiento por su apoyo e integración institucional en el",
            "body2": "2º CONGRESO DE LOGÍSTICA Y TRANSPORTE"
        }
    ]

    for item in certs:
        # Base canvas
        img = Image.new('RGBA', (width, height), (252, 252, 254, 255))
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        d_overlay = ImageDraw.Draw(overlay)

        # Guilloché Security Mesh
        grid_step = 60
        for x in range(-height, width + height, grid_step):
            d_overlay.line([x, 0, x + height, height], fill=(210, 220, 235, 22), width=1)
            d_overlay.line([x, height, x + height, 0], fill=(210, 220, 235, 22), width=1)

        # Waves
        d_overlay.ellipse([-600, -500, 900, 1000], fill=(15, 41, 66, 18))
        d_overlay.ellipse([-500, -400, 750, 850], fill=(0, 168, 204, 25))
        d_overlay.ellipse([-400, -300, 600, 700], fill=(197, 160, 89, 20))
        d_overlay.ellipse([width - 900, height - 1000, width + 600, height + 500], fill=(15, 41, 66, 18))
        d_overlay.ellipse([width - 750, height - 850, width + 500, height + 400], fill=(0, 168, 204, 25))
        d_overlay.ellipse([width - 600, height - 700, width + 400, height + 300], fill=(197, 160, 89, 20))

        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

        # Triple frame
        draw.rectangle([35, 35, width - 35, height - 35], outline=(15, 41, 66, 255), width=8)
        draw.rectangle([48, 48, width - 48, height - 48], outline=(197, 160, 89, 255), width=4)
        draw.rectangle([55, 55, width - 55, height - 55], outline=(212, 175, 55, 255), width=1)
        draw.rectangle([62, 62, width - 62, height - 62], outline=(0, 168, 204, 180), width=2)

        # Corner Filigree
        margin_gold_inner = 55
        corner_len = 50
        for cx, cy in [(margin_gold_inner, margin_gold_inner), 
                       (width - margin_gold_inner, margin_gold_inner), 
                       (margin_gold_inner, height - margin_gold_inner), 
                       (width - margin_gold_inner, height - margin_gold_inner)]:
            dx = 1 if cx < width / 2 else -1
            dy = 1 if cy < height / 2 else -1
            draw.line([cx, cy, cx + (corner_len * dx), cy], fill=(197, 160, 89, 255), width=4)
            draw.line([cx, cy, cx, cy + (corner_len * dy)], fill=(197, 160, 89, 255), width=4)
            diam_size = 6
            draw.polygon([
                (cx + (15 * dx), cy + (15 * dy) - diam_size),
                (cx + (15 * dx) + diam_size, cy + (15 * dy)),
                (cx + (15 * dx), cy + (15 * dy) + diam_size),
                (cx + (15 * dx) - diam_size, cy + (15 * dy))
            ], fill=(197, 160, 89, 255))

        # Logos
        if l_unab:
            u_h = 100
            u_w = int(l_unab.width * (u_h / l_unab.height))
            unab_res = l_unab.resize((u_w, u_h), Image.Resampling.LANCZOS)
            img.paste(unab_res, (110, 95), unab_res)

        if l_cin:
            cin_h = 75
            cin_w = int(l_cin.width * (cin_h / l_cin.height))
            cin_res = l_cin.resize((cin_w, cin_h), Image.Resampling.LANCZOS)
            img.paste(cin_res, (width - 110 - cin_w, 107), cin_res)

        if l_cg2:
            c_h = 105
            c_w = int(l_cg2.width * (c_h / l_cg2.height))
            if c_w > 480:
                c_w = 480
                c_h = int(l_cg2.height * (c_w / l_cg2.width))
            cg2_res = l_cg2.resize((c_w, c_h), Image.Resampling.LANCZOS)
            img.paste(cg2_res, ((width - c_w) // 2, 90), cg2_res)

        # Top Institution Line
        inst_text = "UNIVERSIDAD NACIONAL GUILLERMO BROWN"
        inst_bbox = draw.textbbox((0, 0), inst_text, font=f_inst)
        inst_w = inst_bbox[2] - inst_bbox[0]
        draw.text(((width - inst_w) // 2, 222), inst_text, font=f_inst, fill=(15, 41, 66, 255))

        # Top Gold Divider Line with Diamond
        draw.line([680, 255, 1320, 255], fill=(197, 160, 89, 255), width=2)
        draw.polygon([(1000, 251), (1005, 255), (1000, 259), (995, 255)], fill=(197, 160, 89, 255))

        # Title
        t_bbox = draw.textbbox((0, 0), item["title"], font=f_title)
        t_w = t_bbox[2] - t_bbox[0]
        draw.text(((width - t_w) // 2, 320), item["title"], font=f_title, fill=(15, 41, 66, 255))

        # Subtitle / Intro
        sub_bbox = draw.textbbox((0, 0), item["intro"], font=f_subtitle)
        sub_w = sub_bbox[2] - sub_bbox[0]
        draw.text(((width - sub_w) // 2, 425), item["intro"], font=f_subtitle, fill=(71, 85, 105, 255))

        # Name Underline (at y = 600, with diamond)
        draw.line([320, 600, 1680, 600], fill=(197, 160, 89, 255), width=2)
        draw.line([500, 603, 1500, 603], fill=(15, 41, 66, 180), width=1)
        draw.polygon([(1000, 596), (1007, 600), (1000, 604), (993, 600)], fill=(197, 160, 89, 255))

        # Body text lines (harmoniously spaced)
        b1_bbox = draw.textbbox((0, 0), item["body1"], font=f_body)
        b1_w = b1_bbox[2] - b1_bbox[0]
        draw.text(((width - b1_w) // 2, 670), item["body1"], font=f_body, fill=(51, 65, 85, 255))

        b2_bbox = draw.textbbox((0, 0), item["body2"], font=f_body_highlight)
        b2_w = b2_bbox[2] - b2_bbox[0]
        draw.text(((width - b2_w) // 2, 735), item["body2"], font=f_body_highlight, fill=(15, 41, 66, 255))

        org_line = "organizado por la Universidad Nacional Guillermo Brown"
        org_bbox = draw.textbbox((0, 0), org_line, font=f_body)
        org_w = org_bbox[2] - org_bbox[0]
        draw.text(((width - org_w) // 2, 800), org_line, font=f_body, fill=(51, 65, 85, 255))

        # Date & Location
        date_line = "Burzaco, Almirante Brown, 7 de Noviembre de 2026"
        d_bbox = draw.textbbox((0, 0), date_line, font=f_date)
        d_w = d_bbox[2] - d_bbox[0]
        draw.text(((width - d_w) // 2, 885), date_line, font=f_date, fill=(100, 116, 139, 255))

        # Signature of Rector (centered with slight optical compensation for signature flourish)
        if sig_img:
            s_w = 340
            s_h = int(sig_img.height * (s_w / sig_img.width))
            sig_res = sig_img.resize((s_w, s_h), Image.Resampling.LANCZOS)
            # Center of canvas is 1000. s_w = 340. Offset +15 gives perfect visual optical centering.
            sig_x = (width - s_w) // 2 + 15
            sig_y = 990
            img.paste(sig_res, (sig_x, sig_y), sig_res)

        # Signature Line with gold diamond
        draw.line([700, 1145, 1300, 1145], fill=(15, 41, 66, 255), width=2)
        draw.polygon([(1000, 1142), (1005, 1145), (1000, 1148), (995, 1145)], fill=(197, 160, 89, 255))

        # Rector Name & Title
        r_name = "Lic. Pablo Domenichini"
        rn_bbox = draw.textbbox((0, 0), r_name, font=f_rector_name)
        rn_w = rn_bbox[2] - rn_bbox[0]
        draw.text(((width - rn_w) // 2, 1170), r_name, font=f_rector_name, fill=(15, 41, 66, 255))

        r_title = "Rector — Universidad Nacional Guillermo Brown"
        rt_bbox = draw.textbbox((0, 0), r_title, font=f_rector_title)
        rt_w = rt_bbox[2] - rt_bbox[0]
        draw.text(((width - rt_w) // 2, 1210), r_title, font=f_rector_title, fill=(100, 116, 139, 255))

        # Bottom Bar
        bar_h = 60
        draw.rectangle([0, height - bar_h, width, height], fill=(15, 41, 66, 255))
        draw.line([0, height - bar_h, width, height - bar_h], fill=(197, 160, 89, 255), width=3)

        footer_text = "UNIVERSIDAD NACIONAL GUILLERMO BROWN  •  CONGRESO DE LOGÍSTICA Y TRANSPORTE 2026"
        ft_bbox = draw.textbbox((0, 0), footer_text, font=f_footer)
        ft_w = ft_bbox[2] - ft_bbox[0]
        draw.text(((width - ft_w) // 2, height - bar_h + 18), footer_text, font=f_footer, fill=(255, 255, 255, 255))

        # Save Base Background Template
        bg_out = os.path.join(cert_dir, item["filename"])
        img.convert("RGB").save(bg_out, quality=98)
        print(f"Saved template: {bg_out}")

        # Now create Sample with Name (matching models.py at y = 520)
        sample_img = img.copy().convert("RGB")
        s_draw = ImageDraw.Draw(sample_img)
        sample_name = item["sample_name"]
        
        # Scaling logic exactly as in models.py
        font_size = 65
        while font_size > 20:
            font = ImageFont.truetype(font_path, font_size)
            bbox = s_draw.textbbox((0, 0), sample_name, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width < 1500:
                break
            font_size -= 5

        x = (sample_img.width - text_width) // 2
        y = 520
        s_draw.text((x, y), sample_name, font=font, fill=(15, 41, 66))

        # Save to artifact dir and public dir
        target_art = os.path.join(artifact_dir, item["sample_file"])
        target_pub = os.path.join(public_dir, item["sample_file"])
        sample_img.save(target_art, quality=98)
        sample_img.save(target_pub, quality=98)
        print(f"Saved sample: {target_art}")

if __name__ == "__main__":
    generate_balanced_certificates()
