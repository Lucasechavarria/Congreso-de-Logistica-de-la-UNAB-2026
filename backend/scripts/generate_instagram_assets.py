import os
import math
from PIL import Image, ImageDraw

def create_official_instagram_logo(output_path, size=512):
    # Render at 4x supersampling for ultra-crisp anti-aliasing
    scale = 4
    s = size * scale # 2048x2048
    
    # 1. Create base image with smooth Instagram multi-color gradient
    base = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    
    # Gradient colors
    # We create an angular / radial blended gradient matching official Instagram brand guidelines
    grad = Image.new('RGB', (s, s))
    for y in range(s):
        ny = y / s
        for x in range(s):
            nx = x / s
            
            # Distance from bottom-left corner (0, s) - yellow/orange
            d_bl = math.sqrt(nx**2 + (1 - ny)**2)
            # Distance from top-right corner (s, 0) - purple/blue
            d_tr = math.sqrt((1 - nx)**2 + ny**2)
            
            # Blend
            # Yellow: (254, 218, 55)
            # Orange/Red: (245, 96, 64) -> (225, 48, 108)
            # Magenta/Purple: (193, 53, 132) -> (131, 58, 180)
            # Blue: (88, 81, 219)
            
            # Base linear angle from bottom-left to top-right
            t = (nx + (1 - ny)) / 2.0 # 0 at top-left/bottom-left, 1 at bottom-right/top-right
            
            # Weight for yellow corner at bottom-left
            w_yellow = max(0.0, 1.0 - d_bl * 1.3)
            # Weight for blue corner at top-right
            w_blue = max(0.0, 1.0 - d_tr * 1.4)
            
            # Intermediate magenta/pink
            r = int(225 * (1 - w_blue) + 88 * w_blue)
            g = int(48 * (1 - w_yellow) * (1 - w_blue) + 218 * w_yellow + 81 * w_blue)
            b = int(108 * (1 - w_yellow) * (1 - w_blue) + 55 * w_yellow + 219 * w_blue)
            
            # Enhance vivid saturation
            r = min(255, max(0, int(r * 1.05 + 10)))
            g = min(255, max(0, int(g)))
            b = min(255, max(0, int(b * 1.05)))
            
            grad.putpixel((x, y), (r, g, b))
            
    # Mask rounded rectangle with corner radius = 22.5% of size
    mask = Image.new('L', (s, s), 0)
    d_mask = ImageDraw.Draw(mask)
    radius = int(s * 0.225)
    d_mask.rounded_rectangle([0, 0, s - 1, s - 1], radius=radius, fill=255)
    
    # Apply mask to gradient
    base.paste(grad, (0, 0), mask)
    
    # 2. Draw white camera glyph
    glyph = Image.new('RGBA', (s, s), (255, 255, 255, 0))
    d_glyph = ImageDraw.Draw(glyph)
    
    # Outer rounded box
    box_inset = int(s * 0.18)
    box_w = s - 2 * box_inset
    box_r = int(box_w * 0.28)
    stroke = int(s * 0.065)
    
    d_glyph.rounded_rectangle(
        [box_inset, box_inset, s - box_inset, s - box_inset],
        radius=box_r,
        outline=(255, 255, 255, 255),
        width=stroke
    )
    
    # Center lens circle
    center = s / 2.0
    lens_r = int(s * 0.18)
    d_glyph.ellipse(
        [center - lens_r, center - lens_r, center + lens_r, center + lens_r],
        outline=(255, 255, 255, 255),
        width=stroke
    )
    
    # Flash dot at top-right
    dot_r = int(s * 0.04)
    dot_x = int(s * 0.72)
    dot_y = int(s * 0.28)
    d_glyph.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
        fill=(255, 255, 255, 255)
    )
    
    # Composite glyph onto base
    base = Image.alpha_composite(base, glyph)
    
    # Downscale to target size with high-quality Lanczos resampling
    final = base.resize((size, size), Image.Resampling.LANCZOS)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final.save(output_path, "PNG")
    print(f"Created Instagram official logo at: {output_path}")

def create_white_instagram_glyph(output_path, size=512):
    scale = 4
    s = size * scale
    glyph = Image.new('RGBA', (s, s), (255, 255, 255, 0))
    d_glyph = ImageDraw.Draw(glyph)
    
    # Outer rounded box
    box_inset = int(s * 0.05)
    box_w = s - 2 * box_inset
    box_r = int(box_w * 0.28)
    stroke = int(s * 0.08)
    
    d_glyph.rounded_rectangle(
        [box_inset, box_inset, s - box_inset, s - box_inset],
        radius=box_r,
        outline=(255, 255, 255, 255),
        width=stroke
    )
    
    center = s / 2.0
    lens_r = int(s * 0.24)
    d_glyph.ellipse(
        [center - lens_r, center - lens_r, center + lens_r, center + lens_r],
        outline=(255, 255, 255, 255),
        width=stroke
    )
    
    dot_r = int(s * 0.05)
    dot_x = int(s * 0.75)
    dot_y = int(s * 0.25)
    d_glyph.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
        fill=(255, 255, 255, 255)
    )
    
    final = glyph.resize((size, size), Image.Resampling.LANCZOS)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final.save(output_path, "PNG")
    print(f"Created Instagram white glyph at: {output_path}")

if __name__ == '__main__':
    root_dir = r"c:\Users\User\Desktop\Congreso-UNAB-main"
    out_logo = os.path.join(root_dir, "public", "images", "instagram_official_logo.png")
    out_glyph = os.path.join(root_dir, "public", "images", "instagram_glyph_white.png")
    
    create_official_instagram_logo(out_logo, size=512)
    create_white_instagram_glyph(out_glyph, size=512)
