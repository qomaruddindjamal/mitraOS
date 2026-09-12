#!/usr/bin/env python3
"""
MitraOS Remastered ISO Builder
Founder: Qomaruddin Djamal
Company: Citra Media Technology & Mitra Utama Group
"""

import os
import sys
import re
import json
import shutil
from pathlib import Path
import pycdlib

REPO_ROOT = Path(__file__).resolve().parent.parent

def load_config():
    cfg_file = REPO_ROOT / "build" / "config" / "iso-config.json"
    if cfg_file.exists():
        with open(cfg_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "os_name": "MitraOS",
        "version": "1.0.0",
        "codename": "Apollo",
        "volume_id": "MITRAOS_V1"
    }

def prepare_staging(staging_dir, config):
    print(f"[*] Menyiapkan pohon staging ISO di: {staging_dir}")
    staging = Path(staging_dir)
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True, exist_ok=True)

    # 1. Boot files
    boot_dest = staging / "boot"
    boot_dest.mkdir(parents=True, exist_ok=True)
    
    # Kernel & Initrd
    shutil.copy2(REPO_ROOT / "boot" / "kernel" / "vmlinuz", boot_dest / "vmlinuz")
    shutil.copy2(REPO_ROOT / "boot" / "kernel" / "initrd.img", boot_dest / "initrd.img")

    # GRUB
    grub_dest = boot_dest / "grub"
    grub_dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / "boot" / "grub" / "grub.cfg", grub_dest / "grub.cfg")
    if (REPO_ROOT / "boot" / "grub" / "efi.img").exists():
        shutil.copy2(REPO_ROOT / "boot" / "grub" / "efi.img", grub_dest / "efi.img")

    # ISOLINUX
    isolinux_dest = boot_dest / "isolinux"
    isolinux_dest.mkdir(parents=True, exist_ok=True)
    for item in (REPO_ROOT / "boot" / "isolinux").glob("*"):
        if item.is_file() and item.name.lower() != "boot.cat":
            shutil.copy2(item, isolinux_dest / item.name)

    # 2. EFI Boot
    efi_dest = staging / "EFI" / "BOOT"
    efi_dest.mkdir(parents=True, exist_ok=True)
    if (REPO_ROOT / "boot" / "efi" / "BOOTX64.EFI").exists():
        shutil.copy2(REPO_ROOT / "boot" / "efi" / "BOOTX64.EFI", efi_dest / "BOOTX64.EFI")
    shutil.copy2(REPO_ROOT / "boot" / "grub" / "grub.cfg", efi_dest / "grub.cfg")

    # 3. Core MitraOS System Tree
    mitra_dest = staging / "mitraos"
    mitra_dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(REPO_ROOT / "core" / "bin", mitra_dest / "bin", dirs_exist_ok=True)
    shutil.copytree(REPO_ROOT / "core" / "lib", mitra_dest / "lib", dirs_exist_ok=True)
    shutil.copytree(REPO_ROOT / "core" / "modules", mitra_dest / "modules", dirs_exist_ok=True)

    # 4. Rootfs Overlay & System Configs
    shutil.copytree(REPO_ROOT / "rootfs", staging / "rootfs", dirs_exist_ok=True)
    shutil.copytree(REPO_ROOT / "assets", staging / "assets", dirs_exist_ok=True)
    shutil.copytree(REPO_ROOT / "packages", staging / "packages", dirs_exist_ok=True)

    # 5. Apollo compatibility tree (for library resolution & branding)
    apollo_dest = staging / "apollo"
    apollo_dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(mitra_dest / "bin", apollo_dest / "tools", dirs_exist_ok=True)
    
    # Ensure globals exist in every possible location for scripts
    globals_src = mitra_dest / "lib" / "mitra-globals"
    (apollo_dest / "func").mkdir(parents=True, exist_ok=True)
    shutil.copy2(globals_src, apollo_dest / "func" / "apollo-globals")
    shutil.copy2(globals_src, apollo_dest / "func" / "mitra-globals")
    
    (apollo_dest / "tools" / "func").mkdir(parents=True, exist_ok=True)
    shutil.copy2(globals_src, apollo_dest / "tools" / "func" / "apollo-globals")
    shutil.copy2(globals_src, apollo_dest / "tools" / "func" / "mitra-globals")
    shutil.copy2(globals_src, apollo_dest / "tools" / "mitra-globals")
    shutil.copy2(globals_src, apollo_dest / "tools" / "apollo-globals")

    # In rootfs tree
    (staging / "rootfs" / "boot" / "apollo" / "func").mkdir(parents=True, exist_ok=True)
    shutil.copy2(globals_src, staging / "rootfs" / "boot" / "apollo" / "func" / "apollo-globals")
    shutil.copy2(globals_src, staging / "rootfs" / "boot" / "apollo" / "func" / "mitra-globals")
    shutil.copy2(globals_src, staging / "rootfs" / "boot" / "apollo" / "mitra-globals")
    (staging / "rootfs" / "opt" / "mitraos" / "lib").mkdir(parents=True, exist_ok=True)
    shutil.copy2(globals_src, staging / "rootfs" / "opt" / "mitraos" / "lib" / "mitra-globals")
    (staging / "rootfs" / "bin").mkdir(parents=True, exist_ok=True)
    shutil.copy2(globals_src, staging / "rootfs" / "bin" / "mitra-globals")

    shutil.copytree(REPO_ROOT / "core" / "modules", apollo_dest / "tools" / "modules", dirs_exist_ok=True)
    shutil.copytree(staging / "rootfs", apollo_dest / "rootfs", dirs_exist_ok=True)
    shutil.copytree(REPO_ROOT / "assets" / "branding", apollo_dest / "images", dirs_exist_ok=True)

    # 6. First-Boot Configs
    if (REPO_ROOT / "mitra.txt").exists():
        shutil.copy2(REPO_ROOT / "mitra.txt", staging / "mitra.txt")
        shutil.copy2(REPO_ROOT / "mitra.txt", staging / "apollo.txt")

    print("[+] Pohon staging ISO berhasil disiapkan.")

def sanitize_83(name, existing_names, is_dir=False):
    if is_dir:
        base = name.replace('.', '_')
        ext = ''
    else:
        if '.' in name:
            base, ext = name.rsplit('.', 1)
            ext = '.' + ext
        else:
            base, ext = name, ''
    s_base = re.sub(r'[^A-Z0-9_]', '_', base.upper())[:6]
    s_ext = re.sub(r'[^A-Z0-9]', '', ext.upper())[:3]
    if not s_base:
        s_base = 'D' if is_dir else 'F'
    
    candidate = f"{s_base}.{s_ext}" if s_ext else s_base
    idx = 1
    while candidate in existing_names:
        suffix = f"{idx:02d}"
        trunc = s_base[:8 - len(suffix)]
        candidate = f"{trunc}{suffix}.{s_ext}" if s_ext else f"{trunc}{suffix}"
        idx += 1
    existing_names.add(candidate)
    return candidate

def build_iso_pycdlib(staging_dir, output_path, config):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    vol_id = config.get("volume_id", "MITRAOS_V1")

    print(f"[*] Membuat ISO bootable menggunakan PyCdlib...")
    print(f"    - Target     : {output}")
    print(f"    - Volume ID  : {vol_id}")

    iso = pycdlib.PyCdlib()
    iso.new(interchange_level=3, joliet=3, rock_ridge='1.09', vol_ident=vol_id)

    dir_cache = {"": "/"}
    iso_dir_cache = {"": "/"}
    dir_existing_names = {"/": set()}
    file_iso_map = {}

    staging_path = Path(staging_dir)

    # First pass: Create all directories in sorted order
    for root, dirs, files in os.walk(staging_dir):
        dirs.sort()
        rel = os.path.relpath(root, staging_dir).replace('\\', '/')
        if rel == '.':
            continue
        
        parts = rel.split('/')
        accum_path = ""
        accum_iso = ""
        accum_joliet = ""

        for p in parts:
            prev_path = accum_path
            accum_path = f"{accum_path}/{p}" if accum_path else p
            if accum_path not in dir_cache:
                parent_iso = iso_dir_cache[prev_path]
                if parent_iso not in dir_existing_names:
                    dir_existing_names[parent_iso] = set()
                s_dir = sanitize_83(p, dir_existing_names[parent_iso], is_dir=True)
                curr_iso = f"{parent_iso}/{s_dir}" if parent_iso != '/' else f"/{s_dir}"
                curr_joliet = f"{accum_joliet}/{p}"

                try:
                    iso.add_directory(curr_iso, rr_name=p, joliet_path=curr_joliet)
                except Exception as e:
                    print(f"[!] Warning dir {p} ({curr_iso}): {e}")
                dir_cache[accum_path] = curr_iso
                iso_dir_cache[accum_path] = curr_iso
                dir_existing_names[curr_iso] = set()
                accum_joliet = curr_joliet
            else:
                accum_joliet = f"{accum_joliet}/{p}"

    # Second pass: Add all files
    total_files = 0
    for root, dirs, files in os.walk(staging_dir):
        rel = os.path.relpath(root, staging_dir).replace('\\', '/')
        parent_iso = "/" if rel == "." else iso_dir_cache.get(rel, "/")
        parent_joliet = "" if rel == "." else "/" + rel

        if parent_iso not in dir_existing_names:
            dir_existing_names[parent_iso] = set()

        for f in sorted(files):
            if f.lower() == 'boot.cat':
                continue
            local_fp = os.path.join(root, f)
            rel_file = os.path.relpath(local_fp, staging_dir).replace('\\', '/').lower()
            s_file = sanitize_83(f, dir_existing_names[parent_iso], is_dir=False)
            iso_path = f"{parent_iso}/{s_file};1" if parent_iso != '/' else f"/{s_file};1"
            joliet_path = f"{parent_joliet}/{f}"

            try:
                iso.add_file(local_fp, iso_path, rr_name=f, joliet_path=joliet_path)
                file_iso_map[rel_file] = iso_path
                total_files += 1
            except Exception as e:
                print(f"[!] Warning file {f}: {e}")

    print(f"[+] Total {total_files} file ditambahkan ke dalam sistem berkas ISO.")

    # 3. Add El Torito Boot Configuration
    print("[*] Menambahkan konfigurasi El Torito Dual-Boot (BIOS & UEFI)...")
    isolinux_bin_iso = file_iso_map.get('boot/isolinux/isolinux.bin')
    boot_dir_iso = iso_dir_cache.get('boot', '/BOOT')
    boot_cat_iso = f"{boot_dir_iso}/BOOT.CAT;1"
    if isolinux_bin_iso:
        try:
            iso.add_eltorito(
                isolinux_bin_iso,
                bootcatfile=boot_cat_iso,
                boot_info_table=True,
                media_name='noemul'
            )
            print("    [+] El Torito Legacy BIOS (ISOLINUX) terpasang.")
        except Exception as e:
            print(f"    [!] El Torito BIOS notice: {e}")

    efi_img_iso = file_iso_map.get('boot/grub/efi.img')
    if efi_img_iso:
        try:
            iso.add_eltorito(
                efi_img_iso,
                efi=True,
                media_name='noemul'
            )
            print("    [+] El Torito Modern UEFI (GRUB EFI) terpasang.")
        except Exception as e:
            print(f"    [!] El Torito UEFI notice: {e}")

    # 4. Write Output ISO
    print(f"[*] Menulis image ISO ke disk: {output} ...")
    iso.write(str(output))
    iso.close()

    size_mb = output.stat().st_size / (1024 * 1024)
    print(f"[+] ISO berhasil dibangun: {output} ({size_mb:.1f} MB)")
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="MitraOS ISO Builder")
    parser.add_argument("--output", "-o", default="build/mitraOS_V1.iso", help="Path output file ISO")
    parser.add_argument("--staging", default="build/_staging", help="Direktori staging sementara")
    parser.add_argument("--clean", action="store_true", help="Bersihkan staging setelah selesai")
    parser.add_argument("--dry-run", action="store_true", help="Uji validasi tanpa menulis ISO")

    args = parser.parse_args()
    config = load_config()

    staging_path = REPO_ROOT / args.staging
    output_path = REPO_ROOT / args.output

    try:
        prepare_staging(staging_path, config)
        if args.dry_run:
            print("[+] Validasi staging selesai (dry-run).")
            return 0
        build_iso_pycdlib(staging_path, output_path, config)
        if args.clean:
            shutil.rmtree(staging_path, ignore_errors=True)
            print("[+] Direktori staging dibersihkan.")
        return 0
    except Exception as e:
        print(f"[-] Gagal membangun ISO: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
