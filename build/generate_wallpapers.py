#!/usr/bin/env python3
"""
MitraOS HD Multi-Resolution Wallpaper Generator
Author: Qomaruddin Djamal & Antigravity IDE
Generates razor-sharp, crystal-clear wallpapers from 800x600 up to 4K Ultra HD.
"""

from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_IMG = REPO_ROOT / "assets" / "wallpapers" / "wallpaper.png"

# Target definitions: (width, height, aspect_type, filename)
TARGETS = [
    (3840, 2160, "16:9", "mitra-wallpaper-4k.jpg"),
    (2560, 1440, "16:9", "mitra-wallpaper-2k.jpg"),
    (2560, 1600, "16:10", "mitra-wallpaper-1600p.jpg"),
    (1920, 1080, "16:9", "mitra-wallpaper-1080p.jpg"),
    (1920, 1200, "16:10", "mitra-wallpaper-1200p.jpg"),
    (1366, 768,  "16:9", "mitra-wallpaper-1366x768.jpg"),
    (1280, 720,  "16:9", "mitra-wallpaper-720p.jpg"),
    (1280, 1024, "5:4",  "mitra-wallpaper-1280x1024.jpg"),
    (1024, 768,  "4:3",  "mitra-wallpaper-1024x768.jpg"),
    (800,  600,  "4:3",  "mitra-wallpaper-800x600.jpg"),
]

def enhance_base(img):
    # Dynamic contrast enhancement
    enh_con = ImageEnhance.Contrast(img).enhance(1.06)
    # Color vibrancy for neon cyan & amber
    enh_col = ImageEnhance.Color(enh_con).enhance(1.08)
    return enh_col

def create_aspect_crop(img, target_w, target_h):
    src_w, src_h = img.size
    target_aspect = target_w / target_h
    src_aspect = src_w / src_h
    
    if abs(target_aspect - src_aspect) < 0.02:
        # Near match, scale directly
        return img
    elif target_aspect < src_aspect:
        # Target is narrower (e.g. 4:3 or 5:4 or 16:10 vs 16:9 source)
        # Center-crop width to keep central circular geometry 100% distortion free
        crop_w = int(src_h * target_aspect)
        offset_x = (src_w - crop_w) // 2
        return img.crop((offset_x, 0, offset_x + crop_w, src_h))
    else:
        # Target is wider than source
        crop_h = int(src_w / target_aspect)
        offset_y = (src_h - crop_h) // 2
        return img.crop((0, offset_y, src_w, offset_y + crop_h))

def generate_all():
    print(f"[*] Membaca sumber wallpaper: {SRC_IMG}")
    raw_img = Image.open(SRC_IMG)
    base_img = enhance_base(raw_img)
    
    out_dirs = [
        REPO_ROOT / "assets" / "wallpapers",
        REPO_ROOT / "rootfs" / "usr" / "share" / "mitraos" / "wallpapers"
    ]
    for d in out_dirs:
        d.mkdir(parents=True, exist_ok=True)

    for tw, th, aspect, fname in TARGETS:
        print(f"  -> Memproses {fname} ({tw}x{th}, rasio {aspect})...")
        cropped = create_aspect_crop(base_img, tw, th)
        
        # High quality Lanczos resize
        resized = cropped.resize((tw, th), Image.Resampling.LANCZOS)
        
        # Multi-scale unsharp mask tuned to resolution for crisp geometry
        if tw >= 2560:
            sharpened = resized.filter(ImageFilter.UnsharpMask(radius=2.0, percent=140, threshold=1))
        elif tw >= 1366:
            sharpened = resized.filter(ImageFilter.UnsharpMask(radius=1.5, percent=130, threshold=2))
        else:
            sharpened = resized.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=2))
            
        for d in out_dirs:
            out_file = d / fname
            # Quality 93 provides artifact-free crisp gradients & lines
            sharpened.save(out_file, "JPEG", quality=93, optimize=True)
            
    # Also create standard alias wallpaper.jpg in rootfs (optimized 1024x768 by default for initial boot)
    default_src = out_dirs[1] / "mitra-wallpaper-1024x768.jpg"
    default_dest = REPO_ROOT / "rootfs" / "usr" / "share" / "mitraos" / "wallpaper.jpg"
    import shutil
    shutil.copy2(default_src, default_dest)
    print(f"[+] Wallpaper default 1024x768 diperbarui: {default_dest}")
    print("[+] Semua variasi resolusi wallpaper HD berhasil dibuat!")

if __name__ == "__main__":
    generate_all()
