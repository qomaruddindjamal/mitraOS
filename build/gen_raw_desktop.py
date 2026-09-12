#!/usr/bin/env python3
"""
Generate raw framebuffer images for MitraOS Desktop Environment
"""
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent

def generate_raw_assets():
    src_png = REPO_ROOT / "assets" / "wallpapers" / "desktop_1024.png"
    out_dir = REPO_ROOT / "rootfs" / "usr" / "share" / "mitraos"
    out_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(src_png).convert("RGBA")
    resolutions = [(1024, 768), (800, 600), (1152, 864)]

    for w, h in resolutions:
        if (w, h) == (1024, 768):
            resized = img
        else:
            resized = img.resize((w, h), Image.Resampling.LANCZOS)
        
        # Framebuffer format: BGRA 32-bit (4 bytes per pixel)
        r, g, b, a = resized.split()
        bgra = Image.merge("RGBA", (b, g, r, a))
        raw_bytes = bgra.tobytes()
        
        out_file = out_dir / f"desktop_{w}.raw"
        out_file.write_bytes(raw_bytes)
        print(f"[+] Generated {out_file.name}: {len(raw_bytes):,} bytes ({w}x{h})")

if __name__ == "__main__":
    generate_raw_assets()
