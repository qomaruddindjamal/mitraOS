# MitraOS V.1 (Apollo)

> **Sistem Operasi Multi-Perangkat Modern, Efisien & Ringan Berbasis Linux**  
> **Founder**: Qomaruddin Djamal  
> **Organisasi**: Citra Media Technology & Mitra Utama Group  
> **Arsitektur**: x86_64, ARM64, i686 (Pentium 4 Support), Virtual Machines  

---

## 🌟 Ikhtisar (Overview)

**MitraOS** dirancang untuk memberikan pengalaman komputasi yang cepat, elegan, dan fleksibel baik untuk komputer modern berperforma tinggi maupun perangkat warisan dengan spesifikasi rendah (*vintage/low-spec PC* seperti Pentium 4).

MitraOS menggabungkan fondasi sistem yang stabil, integrasi kecerdasan buatan (**Google Antigravity AI Engine**), manajemen server mandiri, antarmuka desktop modern bergaya **macOS** (Dock & Top Bar) dan **Windows 11** (Snap Layout presisi), serta **23 Menu System Preferences** yang lengkap.

---

## 📂 Struktur Repositori Terorganisir

Repositori MitraOS disusun secara modular, rapi, dan berstandar industri:

```
c:\mitraOS\
├── assets/                     # Koleksi Media & Visual Branding
│   ├── branding/               # Logo resmi, varian monokrom, favicon
│   ├── wallpapers/             # Wallpaper resmi MitraOS
│   └── ui/                     # Komponen grafis tombol (Traffic lights, close/max/min)
├── boot/                       # Konfigurasi Bootloader & Fondasi Kernel
│   ├── grub/                   # GRUB2 UEFI & BIOS (grub.cfg, efi.img)
│   ├── isolinux/               # ISOLINUX BIOS fallback (isolinux.cfg, isolinux.bin)
│   ├── efi/                    # UEFI boot binary (BOOTX64.EFI)
│   └── kernel/                 # Kernel Linux (vmlinuz) & RAM disk (initrd.img)
├── core/                       # Inti Kode Program & Tooling MitraOS
│   ├── bin/                    # Program eksekusi utama CLI & TUI mitra-*
│   │   ├── mitra               # Master CLI entrypoint
│   │   ├── mitra-launcher      # Central Control Center (Menu Utama TUI)
│   │   ├── mitra-preferences   # 23 Menu System Preferences Lengkap
│   │   ├── mitra-snap          # Snap Layout Presisi ala Windows 11
│   │   ├── mitra-desktop       # Switcher Desktop (macOS Dock/Top-bar, Win11, Low-RAM)
│   │   ├── mitra-antigravity   # Hub Google Antigravity AI Agent & Developer Tools
│   │   ├── mitra-asisten       # Remote Web Assistance (ttyd + cloudflared tunnel)
│   │   ├── mitra-software      # Katalog Software Multi-Ekosistem
│   │   ├── mitra-installer     # Disk Installer (HDD / SSD / NVMe / MicroSD)
│   │   ├── mitra-webserver     # Web Server & Database Suite (LEMP, LAMP, Lighttpd)
│   │   ├── mitra-mail          # Email Server Suite (SnappyMail / iRedMail)
│   │   ├── mitra-security      # Hardening & Firewall Manager
│   │   ├── mitra-banner        # Real-time System Monitor & Telemetry
│   │   └── ...                 # Alat pemeliharaan (backup, cleaner, services, update)
│   ├── lib/                    # Shared library fungsi bersama (mitra-globals, tema NEWT)
│   ├── compat/                 # Wrapper kompatibilitas mundur untuk perintah apollo-*
│   └── modules/                # Kernel modules (exfat, vfat, msdos, nls charset)
├── rootfs/                     # Root Filesystem Overlay Sistem MitraOS
│   ├── etc/                    # Konfigurasi sistem (os-release, fastfetch, issue, motd, bashrc.d)
│   ├── usr/                    # Binary overlay (cloudflared, ttyd, parted) & shared assets
│   └── lib/                    # Dynamic linker & library Linux x86_64
├── packages/                   # Manajemen Paket & Katalog Software
│   ├── apt/                    # Shim APT & DPKG ringan, konfigurasi cache 98mitraos
│   └── manifests/              # Manifest fondasi dasar & profil instalasi
│       ├── base-system.manifest# 45+ Paket dasar sistem esensial
│       ├── core-packages.txt   # Utilitas inti sistem
│       ├── developer-suite.txt # Paket lingkungan pengembangan
│       ├── server-suite.txt    # Paket server dan database
│       └── desktop-suite.txt   # Paket antarmuka grafis desktop
├── build/                      # Script Automasi Pembuatan Ulang File ISO
│   ├── build-iso.py            # Builder ISO lintas platform (Python)
│   ├── build-iso.ps1           # Builder ISO native Windows (PowerShell)
│   ├── build-iso.sh            # Builder ISO native Linux (Bash / xorriso)
│   └── config/                 # Konfigurasi metadata ISO (Volume ID, boot flags)
├── docs/                       # Dokumentasi Resmi & Manual MitraOS
│   ├── ARCHITECTURE.md         # Peta arsitektur & struktur folder
│   ├── TOOLS_GUIDE.md          # Panduan lengkap seluruh tool CLI/TUI
│   └── BUILD_GUIDE.md          # Panduan remaster dan compile ISO
├── mitra.txt                   # File konfigurasi otomatis first-boot unattended
└── mitraOS_x86_64Bit_Arm.iso   # File ISO master asli (tetap dipertahankan)
```

---

## 🚀 Fitur Unggulan

### 1. Master CLI `mitra`
Jalankan seluruh perkakas sistem melalui satu pintu perintah:
```bash
mitra launcher       # Buka Control Center utama
mitra preferences    # Buka 23 menu System Preferences
mitra snap           # Atur tata letak jendela (Windows 11 Snap Layout)
mitra desktop        # Beralih tampilan desktop (macOS style dock & top bar)
mitra antigravity    # Hub AI Agent Google Antigravity
mitra asisten        # Aktifkan web assistance & terminal remote
mitra software       # Pasang aplikasi kurasi
mitra installer      # Pasang sistem ke Hard Disk/SSD
mitra banner         # Tampilkan telemetry sistem
```

### 2. Antarmuka Desktop Bergaya macOS (`mitra-desktop`)
- **Top Menu Bar**: Panel atas ramping dengan logo MitraOS, jam, status audio, Wi-Fi, dan telemetry.
- **Centered Floating Dock**: Dock bawah mengapung di tengah layar dengan auto-hide dan animasi hover.
- **Traffic Light Controls**: Tombol kontrol jendela ala macOS (Merah: Tutup, Kuning: Minimize, Hijau: Maximize) di sudut kiri atas titlebar.
- **Glassmorphism Theme**: Tampilan gelap transparan elegan.

### 3. Window Snap Layout Presisi (`mitra-snap`)
- **Split 50/50**: Kiri / Kanan atau Atas / Bawah.
- **Asymmetric 2/3 & 1/3**: Satu jendela kerja utama dan panel samping.
- **Quad 25% Grid**: 4 sudut presisi dengan padding simetris.
- **3 Kolom Sejajar**: 33% / 33% / 33% untuk monitor ultrawide.
- **Center Focus**: Jendela fokus 70% di tengah layar.

### 4. 23 Kategori System Preferences (`mitra-preferences`)
Mencakup seluruh aspek sistem: Appearance, Display, Mouse & Touchpad, Keyboard, Network, Sound, Bluetooth, Printers, Users, Privacy & Security, Software & Updates, Storage, Power, Date & Time, Language, Desktop, Windows, Startup, Accessibility, File Manager, Notifications, Default Applications, dan System Information.

### 5. AI & Developer Hub (`mitra-antigravity`)
Integrasi penuh dengan Google Antigravity AI Agent, CLI (`agy`), Model Context Protocol (MCP), serta lingkungan pemrograman lengkap (Python, Node.js, Go, Rust, C/C++).

---

## 🛠️ Cara Membangun (Build) File ISO

### Menggunakan Python (Cross-Platform)
```bash
python build/build-iso.py --output build/MitraOS-Custom.iso
```

### Menggunakan Windows PowerShell
```powershell
.\build\build-iso.ps1 -Output "build\MitraOS-Custom.iso"
```

### Menggunakan Linux Bash
```bash
bash build/build-iso.sh
```

---

## 📄 Lisensi & Kredit

- **Founder & Arsitek**: Qomaruddin Djamal
- **Perusahaan**: Citra Media Technology & Mitra Utama Group
- **Basis**: Debian GNU/Linux Live System
