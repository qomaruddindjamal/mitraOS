# Panduan Perkakas & Perintah MitraOS (Tools Guide)

Panduan referensi lengkap untuk seluruh program dan perkakas utilitas CLI/TUI di dalam MitraOS.

---

## 1. Master Entrypoint: `mitra`

Perintah `mitra` adalah gerbang utama seluruh utilitas sistem:

```bash
mitra launcher         # Membuka Central Control Center (TUI)
mitra preferences      # Membuka 23 menu System Preferences
mitra snap [layout]    # Mengatur layout jendela presisi
mitra desktop [style]  # Mengubah profil tampilan desktop
mitra antigravity      # Membuka AI Developer & Agent Hub
mitra asisten          # Mengaktifkan remote web assistance & helpdesk
mitra software         # Membuka katalog software terkurasi
mitra installer        # Membuka disk installer ke SSD/HDD
mitra webserver        # Membuka manajer web server (LEMP/LAMP)
mitra mail             # Membuka suite email server
mitra banner           # Menampilkan telemetry monitor sistem
mitra security         # Membuka firewall & security auditor
mitra services         # Mengelola layanan daemon latar belakang
mitra backup           # Menjalankan backup sistem
mitra cleaner          # Membersihkan file sampah & cache
mitra drive            # Mengelola partisi & drive storage
mitra update           # Memeriksa pembaruan MitraOS
mitra version          # Menampilkan versi MitraOS
```

---

## 2. `mitra-preferences` (System Preferences 23 Kategori)

Antarmuka terpadu untuk mengelola seluruh aspek sistem MitraOS:

1. **Appearance**: Mengatur tema dark/slate, mode terang/gelap, warna aksen neon cyan/amber, ikon, font (Inter/SF Pro), dan wallpaper.
2. **Display**: Mengatur resolusi, refresh rate, scaling, multiple display, dan night light.
3. **Mouse & Touchpad**: Kecepatan kursor, akselerasi, natural scrolling, dan gesture touchpad.
4. **Keyboard**: Tata letak keyboard, shortcuts, repeat rate, dan input method.
5. **Network**: Pengaturan Wi-Fi, Ethernet, VPN, Proxy, DNS, dan Firewall.
6. **Sound**: Pilihan output/input audio, volume master, per-application volume, dan sound effects.
7. **Bluetooth**: Pemasangan perangkat BLE, headphone, mouse, dan keyboard.
8. **Printers & Devices**: Konfigurasi printer CUPS, scanner, dan USB devices.
9. **Users & Accounts**: Tambah/edit pengguna, password, hak administrator sudo, dan autologin.
10. **Privacy & Security**: Audit keamanan sistem, permission aplikasi, dan status firewall.
11. **Software & Updates**: Repositori paket, update sistem, dan software center.
12. **Storage**: Partisi disk, mounting filesystem, dan analisis penggunaan penyimpanan.
13. **Power**: Profil daya, timeout layar, sleep, hibernate, dan perilaku tombol power.
14. **Date & Time**: Zona waktu (Asia/Jakarta), sinkronisasi NTP, dan kalender.
15. **Language & Region**: Bahasa sistem, format angka/mata uang, dan format tanggal.
16. **Desktop**: Pemilihan profil desktop (macOS / Windows 11 / Minimal).
17. **Windows**: Perilaku window manager, snap layout, dan traffic lights buttons.
18. **Startup**: Manajemen aplikasi dan daemon yang berjalan otomatis saat boot.
19. **Accessibility**: Skala teks besar, tema high contrast, dan screen reader.
20. **File Manager**: Konfigurasi Thunar/PCManFM, thumbnail preview, dan hidden files.
21. **Notifications**: Posisi notifikasi banner dan mode Do Not Disturb.
22. **Default Applications**: Browser, mail client, file manager, video player, dan terminal bawaan.
23. **System**: Tentang MitraOS, informasi CPU, RAM, Kernel, arsitektur, dan lisensi.

---

## 3. `mitra-snap` (Snap Layout Presisi)

Mengatur posisi dan ukuran jendela aktif secara otomatis:

| Perintah | Deskripsi Tata Letak |
|----------|----------------------|
| `mitra snap left` | Membagi layar 50% di sebelah kiri |
| `mitra snap right` | Membagi layar 50% di sebelah kanan |
| `mitra snap top` | Membagi layar 50% di sebelah atas |
| `mitra snap bottom` | Membagi layar 50% di sebelah bawah |
| `mitra snap top-left` | Memposisikan jendela 25% di sudut kiri atas |
| `mitra snap top-right` | Memposisikan jendela 25% di sudut kanan atas |
| `mitra snap bottom-left` | Memposisikan jendela 25% di sudut kiri bawah |
| `mitra snap bottom-right` | Memposisikan jendela 25% di sudut kanan bawah |
| `mitra snap left-23` | Jendela utama 66% di kiri (asimetris) |
| `mitra snap right-13` | Panel samping 33% di kanan (asimetris) |
| `mitra snap center` | Jendela mengapung fokus 70% di tengah layar |
| `mitra snap col1` / `col2` / `col3` | Tata letak 3 kolom sejajar (masing-masing 33%) |
| `mitra snap max` | Maksimalkan jendela layar penuh |
| `mitra snap menu` | Buka menu visual selector layout |

---

## 4. `mitra-desktop` (Desktop Switcher)

Mengubah tampilan antarmuka visual desktop secara instan:

```bash
mitra-desktop --macos       # Aktifkan tampilan gaya macOS (Top Bar + Centered Dock + Traffic Lights)
mitra-desktop --win11       # Aktifkan tampilan gaya Windows 11 (Centered Taskbar)
mitra-desktop --lowram      # Aktifkan tampilan ultra-ringan Openbox (<35 MB RAM)
mitra-desktop --wallpaper   # Buka pemilih wallpaper resmi MitraOS
```

---

## 5. `mitra-antigravity` (Google Antigravity AI Hub)

- Integrasi alat AI Developer Google Antigravity.
- Manajemen agen Model Context Protocol (MCP).
- Pemasangan tool pengembang: Python, Node.js, Go, Rust, Neovim, Git, dan CLI `agy`.

---

## 6. `mitra-asisten` (Remote Web Assistance)

- Menjalankan terminal web `ttyd` yang aman di port lokal.
- Membuka Cloudflare Tunnel terenkripsi otomatis dengan URL publik acak untuk akses helpdesk jarak jauh tanpa memerlukan IP publik statis.
