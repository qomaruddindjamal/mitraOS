# Panduan Membangun & Membakar File ISO MitraOS (Build Guide)

Panduan langkah demi langkah untuk meremaster, memvalidasi, dan mengkompilasi file ISO bootable MitraOS.

---

## 1. Prasyarat Lingkungan

### Di Sistem Windows:
- **Python 3.8+** (terpasang di PATH)
- **7-Zip** (`7z.exe` di PATH atau lokasi default)
- **PowerShell 5.1+**

### Di Sistem Linux:
- **Python 3.8+**
- **xorriso** (`sudo apt-get install xorriso`)
- **isolinux** & **mtools**

---

## 2. Validasi Struktur (Dry-Run)

Sebelum membuat file ISO penuh, jalankan uji coba validasi struktur pohon:

```bash
python build/build-iso.py --dry-run
```

Output yang berhasil akan menampilkan kesiapan kernel `/boot/vmlinuz`, initrd `/boot/initrd.img`, konfigurasi GRUB/ISOLINUX, dan pohon staging tanpa error.

---

## 3. Membangun File ISO (Compile)

### Cara 1: Menggunakan Python (Cross-Platform)
```bash
python build/build-iso.py --output build/MitraOS-1.0-x86_64.iso --clean
```

### Cara 2: Menggunakan Windows PowerShell
```powershell
.\build\build-iso.ps1 -Output "build\MitraOS-1.0-x86_64.iso" -Clean
```

### Cara 3: Menggunakan Linux Bash
```bash
bash build/build-iso.sh build/MitraOS-1.0-x86_64.iso
```

---

## 4. Menulis ISO ke Media USB / Flashdisk

### Di Windows:
Gunakan **Rufus** (https://rufus.ie):
1. Masukkan Flashdisk USB (minimal 1 GB).
2. Buka Rufus dan pilih file ISO yang dihasilkan.
3. Skema Partisi: **GPT** (untuk UEFI) atau **MBR** (untuk BIOS/Legacy).
4. Klik **Mulai (Start)**.

### Di Linux:
Gunakan perintah `dd`:
```bash
sudo dd if=build/MitraOS-1.0-x86_64.iso of=/dev/sdX bs=4M status=progress conv=fdatasync
```
*(Ganti `/dev/sdX` dengan identifier perangkat USB Anda)*.

---

## 5. Menguji File ISO di Mesin Virtual (QEMU / VirtualBox)

### Menggunakan QEMU:
```bash
qemu-system-x86_64 -m 2048 -cdrom build/MitraOS-1.0-x86_64.iso -boot d -enable-kvm
```

### Menggunakan VirtualBox / VMware / Hyper-V:
1. Buat Virtual Machine baru tipe Linux (Debian 64-bit).
2. Alokasikan RAM 1024 MB – 2048 MB.
3. Pasang file ISO `MitraOS-1.0-x86_64.iso` sebagai optical drive.
4. Nyalakan VM dan nikmati MitraOS Live Session.
