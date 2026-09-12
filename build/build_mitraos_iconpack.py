import os
import math
from PIL import Image

SRC_PATH = r'C:\Users\Administrator\.gemini\antigravity-ide\brain\1ea60939-1e52-44b3-a21f-039a0151abea\.user_uploaded\media_1789226723521.png'
BASE_OUT = r'C:\mitraOS\assets\icons\mitraos-iconpack'

SIZES = [256, 128, 64, 48, 32]

# Definition of all 45 icons with exact coordinate bounding boxes
ICONS = [
    # --- LOGO & BRANDING ---
    {
        'category': 'logo',
        'name': 'mitraos-logo',
        'desc': 'MitraOS Primary Brand Hexagon M Icon',
        'bbox': (24, 17, 120, 114)
    },
    {
        'category': 'logo',
        'name': 'mitraos-iconpack-banner',
        'desc': 'MitraOS Icon Pack Brand Header Banner',
        'bbox': (24, 17, 360, 115)
    },

    # --- SYSTEM PREFERENCES (16 ICONS) ---
    {
        'category': 'system-preferences',
        'name': 'preferences-system',
        'desc': 'Umum (General / System Settings)',
        'bbox': (37, 196, 92, 251)
    },
    {
        'category': 'system-preferences',
        'name': 'preferences-desktop-display',
        'desc': 'Tampilan (Display & Resolution)',
        'bbox': (125, 197, 184, 252)
    },
    {
        'category': 'system-preferences',
        'name': 'audio-volume-high',
        'desc': 'Suara (Sound & Audio Settings)',
        'bbox': (219, 201, 272, 247)
    },
    {
        'category': 'system-preferences',
        'name': 'preferences-system-network',
        'desc': 'Jaringan (Network & Internet)',
        'bbox': (303, 197, 356, 251)
    },
    {
        'category': 'system-preferences',
        'name': 'preferences-system-bluetooth',
        'desc': 'Bluetooth (Wireless Devices)',
        'bbox': (40, 301, 92, 358)
    },
    {
        'category': 'system-preferences',
        'name': 'drive-removable-media',
        'desc': 'Perangkat (Devices & USB)',
        'bbox': (132, 303, 175, 356)
    },
    {
        'category': 'system-preferences',
        'name': 'system-users',
        'desc': 'Akun (User Accounts)',
        'bbox': (217, 303, 266, 356)
    },
    {
        'category': 'system-preferences',
        'name': 'preferences-security',
        'desc': 'Keamanan (Security & Firewall)',
        'bbox': (305, 303, 353, 357)
    },
    {
        'category': 'system-preferences',
        'name': 'preferences-system-time',
        'desc': 'Tanggal & Waktu (Date & Time)',
        'bbox': (39, 413, 93, 467)
    },
    {
        'category': 'system-preferences',
        'name': 'preferences-desktop-locale',
        'desc': 'Bahasa (Language & Region)',
        'bbox': (126, 412, 186, 467)
    },
    {
        'category': 'system-preferences',
        'name': 'system-software-update',
        'desc': 'Pembaruan (Software Updates)',
        'bbox': (218, 417, 265, 464)
    },
    {
        'category': 'system-preferences',
        'name': 'applications-other',
        'desc': 'Aplikasi (Applications & Apps)',
        'bbox': (304, 415, 357, 466)
    },
    {
        'category': 'system-preferences',
        'name': 'preferences-system-privacy',
        'desc': 'Privasi (Privacy & Permissions)',
        'bbox': (40, 527, 92, 585)
    },
    {
        'category': 'system-preferences',
        'name': 'preferences-system-power',
        'desc': 'Daya (Power & Battery)',
        'bbox': (136, 529, 173, 583)
    },
    {
        'category': 'system-preferences',
        'name': 'preferences-system-hardware',
        'desc': 'Sistem (Hardware & CPU)',
        'bbox': (218, 531, 271, 585)
    },
    {
        'category': 'system-preferences',
        'name': 'help-about',
        'desc': 'Tentang (About MitraOS)',
        'bbox': (304, 532, 356, 585)
    },

    # --- FOLDERS (12 ICONS) ---
    {
        'category': 'folders',
        'name': 'folder',
        'desc': 'Folder (Standard Blue Directory)',
        'bbox': (401, 192, 467, 248)
    },
    {
        'category': 'folders',
        'name': 'folder-documents',
        'desc': 'Dokumen (Documents Folder)',
        'bbox': (496, 192, 559, 248)
    },
    {
        'category': 'folders',
        'name': 'folder-pictures',
        'desc': 'Gambar (Pictures / Photos Folder)',
        'bbox': (588, 193, 652, 248)
    },
    {
        'category': 'folders',
        'name': 'folder-music',
        'desc': 'Musik (Music & Audio Folder)',
        'bbox': (680, 192, 744, 249)
    },
    {
        'category': 'folders',
        'name': 'folder-videos',
        'desc': 'Video (Movies & Video Folder)',
        'bbox': (401, 289, 468, 347)
    },
    {
        'category': 'folders',
        'name': 'folder-download',
        'desc': 'Unduhan (Downloads Folder)',
        'bbox': (495, 290, 559, 347)
    },
    {
        'category': 'folders',
        'name': 'folder-favorites',
        'desc': 'Favorit (Favorites / Starred Folder)',
        'bbox': (588, 290, 652, 347)
    },
    {
        'category': 'folders',
        'name': 'folder-locked',
        'desc': 'Terkunci (Encrypted / Locked Folder)',
        'bbox': (680, 290, 745, 347)
    },
    {
        'category': 'folders',
        'name': 'folder-new',
        'desc': 'Folder Baru (New Folder Action)',
        'bbox': (402, 393, 467, 446)
    },
    {
        'category': 'folders',
        'name': 'folder-delete',
        'desc': 'Hapus (Delete Folder Action)',
        'bbox': (496, 393, 560, 446)
    },
    {
        'category': 'folders',
        'name': 'folder-search',
        'desc': 'Cari (Search Folder Action)',
        'bbox': (588, 393, 652, 446)
    },
    {
        'category': 'folders',
        'name': 'folder-home',
        'desc': 'Beranda (Home Directory)',
        'bbox': (680, 393, 745, 446)
    },

    # --- WORKSTATION = EXPLORER (7 ICONS) ---
    {
        'category': 'workstation',
        'name': 'workstation-explorer',
        'desc': 'Explorer (Mitra Explorer File Manager)',
        'bbox': (403, 552, 460, 601)
    },
    {
        'category': 'workstation',
        'name': 'computer',
        'desc': 'This PC (My Computer / System Root)',
        'bbox': (491, 548, 542, 601)
    },
    {
        'category': 'workstation',
        'name': 'network-workgroup',
        'desc': 'Network (Network Places & Shares)',
        'bbox': (553, 548, 628, 601)
    },
    {
        'category': 'workstation',
        'name': 'user-trash',
        'desc': 'Recycle Bin (Trash / Tempat Sampah)',
        'bbox': (663, 548, 705, 601)
    },
    {
        'category': 'workstation',
        'name': 'folder-saved-search',
        'desc': 'Libraries (Media Libraries Group)',
        'bbox': (750, 553, 796, 601)
    },
    {
        'category': 'workstation',
        'name': 'preferences-system-control-panel',
        'desc': 'Control Panel (System Quick Settings)',
        'bbox': (836, 550, 886, 601)
    },
    {
        'category': 'workstation',
        'name': 'system-search',
        'desc': 'Search (Spotlight Search Tool)',
        'bbox': (930, 550, 976, 601)
    },

    # --- POINTERS / CURSORS (9 ICONS) ---
    {
        'category': 'pointers',
        'name': 'pointer-normal',
        'desc': 'Normal (Default Blue Arrow Pointer)',
        'bbox': (794, 195, 830, 248)
    },
    {
        'category': 'pointers',
        'name': 'pointer-text',
        'desc': 'Teks (I-Beam Text Selection Cursor)',
        'bbox': (876, 196, 899, 244)
    },
    {
        'category': 'pointers',
        'name': 'pointer-hand',
        'desc': 'Tangan (Hand Link Click Pointer)',
        'bbox': (942, 194, 984, 246)
    },
    {
        'category': 'pointers',
        'name': 'pointer-resize',
        'desc': 'Resize (Diagonal Window Sizing Cursor)',
        'bbox': (794, 298, 827, 342)
    },
    {
        'category': 'pointers',
        'name': 'pointer-move',
        'desc': 'Pindah (4-Way Move Window Cursor)',
        'bbox': (868, 294, 909, 342)
    },
    {
        'category': 'pointers',
        'name': 'pointer-wait',
        'desc': 'Tunggu (Busy Loading Spinner Ring)',
        'bbox': (944, 293, 984, 342)
    },
    {
        'category': 'pointers',
        'name': 'pointer-crosshair',
        'desc': 'Crosshair (Precision Target Cursor)',
        'bbox': (791, 398, 835, 447)
    },
    {
        'category': 'pointers',
        'name': 'pointer-forbidden',
        'desc': 'Dilarang (Not Allowed / Stop Cursor)',
        'bbox': (868, 398, 910, 447)
    },
    {
        'category': 'pointers',
        'name': 'pointer-help',
        'desc': 'Bantuan (Arrow with Question Help Cursor)',
        'bbox': (944, 398, 987, 447)
    }
]

def remove_background_clean(im, thresh=24, soft_thresh=42):
    im = im.convert('RGBA')
    w, h = im.size
    pix = im.load()
    
    # Calculate background from border pixels
    edge_pixels = []
    for x in range(w):
        edge_pixels.append(pix[x, 0][:3])
        edge_pixels.append(pix[x, h-1][:3])
    for y in range(h):
        edge_pixels.append(pix[0, y][:3])
        edge_pixels.append(pix[w-1, y][:3])
        
    bg_r = sum(p[0] for p in edge_pixels) / len(edge_pixels)
    bg_g = sum(p[1] for p in edge_pixels) / len(edge_pixels)
    bg_b = sum(p[2] for p in edge_pixels) / len(edge_pixels)
    edge_bg = (bg_r, bg_g, bg_b)
    
    # Flood-fill from borders
    visited = set()
    to_visit = []
    for x in range(w):
        to_visit.append((x, 0))
        to_visit.append((x, h-1))
    for y in range(h):
        to_visit.append((0, y))
        to_visit.append((w-1, y))
        
    def dist(c1, c2):
        return math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2)
        
    while to_visit:
        cx, cy = to_visit.pop()
        if (cx, cy) in visited or cx < 0 or cx >= w or cy < 0 or cy >= h:
            continue
        visited.add((cx, cy))
        p = pix[cx, cy]
        if dist(p[:3], edge_bg) < soft_thresh:
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in visited:
                    to_visit.append((nx, ny))
                    
    # Set transparency
    for y in range(h):
        for x in range(w):
            if (x, y) in visited:
                p = pix[x, y]
                d = dist(p[:3], edge_bg)
                if d <= thresh:
                    pix[x, y] = (p[0], p[1], p[2], 0)
                elif d < soft_thresh:
                    alpha = int(255 * ((d - thresh) / (soft_thresh - thresh))**1.2)
                    pix[x, y] = (p[0], p[1], p[2], min(255, max(0, alpha)))
                    
    # Auto-crop transparent boundaries
    bbox = im.getbbox()
    if bbox:
        trimmed = im.crop(bbox)
        tw, th = trimmed.size
        # Make a balanced square with 8% padding
        side = int(max(tw, th) * 1.16)
        square = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        ox = (side - tw) // 2
        oy = (side - th) // 2
        square.paste(trimmed, (ox, oy), trimmed)
        return square
    return im

def main():
    print(f"[*] Membaca lembar Icon Pack MitraOS dari: {SRC_PATH}")
    src_img = Image.open(SRC_PATH).convert('RGBA')
    
    # Create output directories
    for sub in ['master'] + [f"{sz}x{sz}" for sz in SIZES]:
        for cat in ['logo', 'system-preferences', 'folders', 'workstation', 'pointers']:
            os.makedirs(os.path.join(BASE_OUT, sub, cat), exist_ok=True)
            
    catalog_entries = []
    print(f"[*] Memproses dan mengekstrak {len(ICONS)} ikon...")
    
    for idx, item in enumerate(ICONS, 1):
        cat = item['category']
        name = item['name']
        desc = item['desc']
        bx1, by1, bx2, by2 = item['bbox']
        
        # Crop raw region
        raw_crop = src_img.crop((bx1, by1, bx2, by2))
        
        # Remove background & smooth
        clean_img = remove_background_clean(raw_crop)
        
        # Save master PNG
        master_path = os.path.join(BASE_OUT, 'master', cat, f"{name}.png")
        clean_img.save(master_path, format='PNG', optimize=True)
        
        # Generate standard sizes: 256, 128, 64, 48, 32
        for sz in SIZES:
            resized = clean_img.resize((sz, sz), Image.Resampling.LANCZOS)
            sz_path = os.path.join(BASE_OUT, f"{sz}x{sz}", cat, f"{name}.png")
            resized.save(sz_path, format='PNG', optimize=True)
            
        print(f"  [{idx:02d}/{len(ICONS)}] {cat:20s} -> {name}.png ({clean_img.width}x{clean_img.height})")
        catalog_entries.append({
            'index': idx,
            'category': cat,
            'name': name,
            'desc': desc,
            'file': f"{cat}/{name}.png"
        })

    # Generate CATALOG.md
    print("[*] Membuat berkas dokumentasi katalog ikon (CATALOG.md)...")
    catalog_path = os.path.join(BASE_OUT, "CATALOG.md")
    with open(catalog_path, "w", encoding="utf-8") as f:
        f.write("# MitraOS Official Icon Pack Collection\n\n")
        f.write("> **Desain**: Modern, Sederhana, dan Konsisten untuk Pengalaman Kerja yang Lebih Baik.\n")
        f.write("> **Status**: Aset siap digunakan (disimpan di `assets/icons/mitraos-iconpack/`, **belum diterapkan** ke konfigurasi Desktop Environment sesuai instruksi).\n\n")
        f.write("## Ringkasan Paket Ikon\n\n")
        f.write(f"- **Total Ikon**: {len(ICONS)} buah\n")
        f.write("- **Format Berkas**: PNG Transparan (Alpha Channel 32-bit RGBA)\n")
        f.write("- **Resolusi Tersedia**: Master Asli, 256x256, 128x128, 64x64, 48x48, 32x32\n\n")
        f.write("## Daftar Ikon Berdasarkan Kategori\n\n")
        f.write("| No | Kategori | Nama Berkas | Keterangan / Penggunaan |\n")
        f.write("|:--:|:---------|:------------|:------------------------|\n")
        for entry in catalog_entries:
            f.write(f"| {entry['index']:02d} | `{entry['category']}` | `{entry['name']}.png` | {entry['desc']} |\n")
        f.write("\n## Struktur Direktori Aset\n\n")
        f.write("```\n")
        f.write("assets/icons/mitraos-iconpack/\n")
        f.write("├── CATALOG.md\n")
        f.write("├── master/                # Resolusi Master Asli (Transparan)\n")
        f.write("├── 256x256/               # Format High-DPI Desktop\n")
        f.write("├── 128x128/               # Format App Hub & Control Center\n")
        f.write("├── 64x64/                 # Format Desktop Icons & Window Headers\n")
        f.write("├── 48x48/                 # Format Floating Dock\n")
        f.write("└── 32x32/                 # Format Top Menubar & Tray\n")
        f.write("```\n")
        
    print(f"[+] Berhasil membuat seluruh {len(ICONS)} ikon dan katalog di {BASE_OUT}!")

if __name__ == "__main__":
    main()
