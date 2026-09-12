#!/usr/bin/env python3
"""
generate_complementary_icons.py
Membuat ikon pelengkap resmi MitraOS System Preferences yang serasi:
1. preferences-system-mouse.png (Mouse & Touchpad)
2. audio-volume-muted.png (Mute Audio)
3. network-wireless.png (Wi-Fi Nirkabel)
4. preferences-desktop-wallpaper.png (Wallpaper & Personalisasi)
5. go-previous.png / arrow-left.png (Tombol Kembali)
"""

import os
from PIL import Image, ImageDraw, ImageFilter

SIZES = [256, 128, 64, 48, 32]
BASE_DIR = r"c:\mitraOS\assets\icons\mitraos-iconpack"

def create_mouse_icon():
    # 256x256 master
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Soft shadow
    shadow = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle([76, 56, 180, 216], radius=52, fill=(0, 30, 80, 50))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(shadow)

    # Mouse body (Gradient from #37474F to #263238 or Blue #1E88E5 to #1565C0)
    # Using MitraOS slate-blue gradient
    for y in range(50, 210):
        ratio = (y - 50) / 160.0
        # Color transition from Slate-Blue to Darker Blue-Gray
        r = int(55 * (1 - ratio) + 26 * ratio)
        g = int(90 * (1 - ratio) + 50 * ratio)
        b = int(140 * (1 - ratio) + 95 * ratio)
        draw.line([(78, y), (178, y)], fill=(r, g, b, 255))

    # Mask to rounded rectangle
    mask = Image.new("L", (256, 256), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([78, 50, 178, 210], radius=50, fill=255)
    
    # Apply mask
    body = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(body)
    # Re-draw with gradient on masked surface
    for y in range(50, 210):
        ratio = (y - 50) / 160.0
        r = int(70 * (1 - ratio) + 38 * ratio)
        g = int(115 * (1 - ratio) + 68 * ratio)
        b = int(175 * (1 - ratio) + 120 * ratio)
        bdraw.line([(78, y), (178, y)], fill=(r, g, b, 255))
    
    # Specular gloss on top
    gdraw = ImageDraw.Draw(body)
    gdraw.arc([88, 56, 168, 120], start=190, end=350, fill=(255, 255, 255, 100), width=4)
    
    # Center divider line
    bdraw.line([(128, 52), (128, 110)], fill=(25, 45, 75, 200), width=3)
    
    # Scroll wheel (Glowing Cyan)
    bdraw.rounded_rectangle([122, 70, 134, 102], radius=6, fill=(0, 210, 255, 255))
    bdraw.rounded_rectangle([124, 74, 132, 98], radius=4, fill=(255, 255, 255, 220))
    
    # Subtle touchpad arc indicator near base
    bdraw.arc([98, 150, 158, 190], start=20, end=160, fill=(180, 210, 245, 120), width=3)

    img.paste(body, (0, 0), mask)
    return img

def create_muted_icon():
    # Base from audio-volume-high if exists
    src = os.path.join(BASE_DIR, "master", "system-preferences", "audio-volume-high.png")
    if os.path.exists(src):
        img = Image.open(src).convert("RGBA")
    else:
        img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    
    # Draw soft red slash
    draw = ImageDraw.Draw(img)
    # Red diagonal line with shadow
    draw.line([(45, 45), (211, 211)], fill=(220, 50, 60, 240), width=18)
    draw.line([(45, 45), (211, 211)], fill=(255, 100, 100, 255), width=10)
    return img

def create_wifi_icon():
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Shadow
    shadow = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.arc([36, 46, 220, 230], start=215, end=325, fill=(0, 70, 160, 60), width=24)
    sdraw.arc([66, 86, 190, 210], start=215, end=325, fill=(0, 70, 160, 60), width=22)
    sdraw.arc([96, 126, 160, 190], start=215, end=325, fill=(0, 70, 160, 60), width=20)
    sdraw.ellipse([114, 186, 142, 214], fill=(0, 70, 160, 60))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(shadow)

    # Arcs - Blue Cyan Gradient style
    draw.arc([36, 40, 220, 224], start=215, end=325, fill=(30, 144, 255, 255), width=20)
    draw.arc([66, 80, 190, 204], start=215, end=325, fill=(0, 180, 240, 255), width=18)
    draw.arc([96, 120, 160, 184], start=215, end=325, fill=(0, 210, 255, 255), width=16)
    draw.ellipse([116, 180, 140, 204], fill=(0, 160, 255, 255))
    draw.ellipse([120, 184, 136, 200], fill=(255, 255, 255, 230))
    return img

def create_back_icon():
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Circle background
    draw.ellipse([30, 30, 226, 226], fill=(40, 90, 160, 220))
    draw.ellipse([34, 34, 222, 222], fill=(25, 60, 115, 255))
    # Left arrow
    draw.line([(150, 75), (95, 128)], fill=(255, 255, 255, 255), width=18)
    draw.line([(95, 128), (150, 181)], fill=(255, 255, 255, 255), width=18)
    draw.line([(100, 128), (175, 128)], fill=(255, 255, 255, 255), width=18)
    return img

def main():
    icons = {
        "preferences-system-mouse.png": create_mouse_icon(),
        "audio-volume-muted.png": create_muted_icon(),
        "network-wireless.png": create_wifi_icon(),
        "arrow-left.png": create_back_icon(),
    }

    for name, master_img in icons.items():
        # Save master
        m_path = os.path.join(BASE_DIR, "master", "system-preferences", name)
        os.makedirs(os.path.dirname(m_path), exist_ok=True)
        master_img.save(m_path, "PNG")
        print(f"[+] Master: {name}")

        # Scale to all sizes
        for sz in SIZES:
            s_img = master_img.resize((sz, sz), Image.Resampling.LANCZOS)
            out_p = os.path.join(BASE_DIR, f"{sz}x{sz}", "system-preferences", name)
            os.makedirs(os.path.dirname(out_p), exist_ok=True)
            s_img.save(out_p, "PNG")
            print(f"  -> {sz}x{sz}: {name}")

    print("\n[+] Selesai membuat ikon pelengkap resmi MitraOS System Preferences!")

if __name__ == "__main__":
    main()
