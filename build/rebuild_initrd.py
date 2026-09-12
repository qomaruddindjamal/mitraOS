#!/usr/bin/env python3
"""
MitraOS Initrd Patcher & Rebuilder
Founder: Qomaruddin Djamal
Company: Citra Media Technology & Mitra Utama Group
"""

import io
import time
from pathlib import Path
import zstandard as zstd

REPO_ROOT = Path(__file__).resolve().parent.parent

def parse_cpio(data):
    pos = 0
    entries = {}
    while pos + 110 <= len(data):
        magic = data[pos:pos+6]
        if magic not in (b'070701', b'070702'):
            next_pos = data.find(b'070701', pos)
            if next_pos != -1:
                pos = next_pos
                continue
            break
        header = data[pos:pos+110]
        mode = int(header[14:22], 16)
        uid = int(header[22:30], 16)
        gid = int(header[30:38], 16)
        nlink = int(header[38:46], 16)
        mtime = int(header[46:54], 16)
        filesize = int(header[54:62], 16)
        namesize = int(header[94:102], 16)
        name = data[pos+110:pos+110+namesize-1].decode('utf-8', errors='ignore')
        name_pad = (4 - ((110 + namesize) % 4)) % 4
        content_start = pos + 110 + namesize + name_pad
        content_pad = (4 - (filesize % 4)) % 4
        pos = content_start + filesize + content_pad
        if name == 'TRAILER!!!':
            continue
        content = data[content_start:content_start+filesize]
        entries[name] = {
            'mode': mode, 'uid': uid, 'gid': gid, 'nlink': nlink,
            'mtime': mtime, 'content': content
        }
    return entries

def make_cpio(entries):
    out = io.BytesIO()
    ino = 1
    for name, entry in entries.items():
        name_bytes = name.encode('utf-8') + b'\0'
        content = entry['content']
        namesize = len(name_bytes)
        filesize = len(content)
        mode = entry.get('mode', 0o100755)
        uid = entry.get('uid', 0)
        gid = entry.get('gid', 0)
        nlink = entry.get('nlink', 1)
        mtime = entry.get('mtime', int(time.time()))
        
        hdr = f"070701{ino:08x}{mode:08x}{uid:08x}{gid:08x}{nlink:08x}{mtime:08x}{filesize:08x}00000000000000000000000000000000{namesize:08x}00000000".encode('ascii')
        out.write(hdr)
        out.write(name_bytes)
        name_pad = (4 - ((110 + namesize) % 4)) % 4
        out.write(b'\0' * name_pad)
        out.write(content)
        content_pad = (4 - (filesize % 4)) % 4
        out.write(b'\0' * content_pad)
        ino += 1
    
    trailer_name = b'TRAILER!!!\0'
    t_namesize = len(trailer_name)
    hdr = f"0707010000000000000000000000000000000000000001000000000000000000000000000000000000000000000000{t_namesize:08x}00000000".encode('ascii')
    out.write(hdr)
    out.write(trailer_name)
    t_pad = (4 - ((110 + t_namesize) % 4)) % 4
    out.write(b'\0' * t_pad)
    pad_512 = (512 - (out.tell() % 512)) % 512
    out.write(b'\0' * pad_512)
    return out.getvalue()

def patch_initrd():
    print("[*] Membaca arsip initrd...")
    cpio_path = REPO_ROOT / "build" / "initrd.cpio"
    if not cpio_path.exists():
        initrd_img = REPO_ROOT / "boot" / "kernel" / "initrd.img"
        with open(initrd_img, "rb") as f:
            dctx = zstd.ZstdDecompressor()
            decompressed = dctx.decompress(f.read(), max_output_size=500*1024*1024)
        with open(cpio_path, "wb") as f:
            f.write(decompressed)

    with open(cpio_path, "rb") as f:
        entries = parse_cpio(f.read())
    print(f"[+] Total {len(entries)} entri terbaca dari initrd cpio.")

    # 0. Purge all legacy apollo executable commands from base initrd
    purged_apollo = []
    for k in list(entries.keys()):
        if any(k.startswith(p) for p in ["bin/apollo", "usr/bin/apollo", "sbin/apollo", "boot/apollo/apollo"]):
            if k == "boot/apollo/func/apollo-globals":
                continue
            purged_apollo.append(k)
            del entries[k]
    if purged_apollo:
        print(f"[+] Dihapus {len(purged_apollo)} perintah apollo lama dari initrd.")

    # Injeksi hostname & hosts
    entries["etc/hostname"] = {
        'mode': 0o100644, 'uid': 0, 'gid': 0, 'nlink': 1,
        'mtime': int(time.time()), 'content': b'apollo\n'
    }
    entries["etc/hosts"] = {
        'mode': 0o100644, 'uid': 0, 'gid': 0, 'nlink': 1,
        'mtime': int(time.time()),
        'content': b'127.0.0.1\tlocalhost\n127.0.1.1\tapollo\n::1\t\tlocalhost ip6-localhost ip6-loopback\n'
    }

    # 1. Update globals
    globals_file = REPO_ROOT / "core" / "lib" / "mitra-globals"
    globals_bytes = globals_file.read_bytes()

    for path in [
        "boot/apollo/func/mitra-globals",
        "boot/apollo/func/apollo-globals",
        "boot/apollo/mitra-globals",
        "opt/mitraos/lib/mitra-globals",
        "boot/mitraos/func/mitra-globals",
        "bin/mitra-globals",
        "usr/bin/mitra-globals"
    ]:
        entries[path] = {
            'mode': 0o100755, 'uid': 0, 'gid': 0, 'nlink': 1,
            'mtime': int(time.time()), 'content': globals_bytes
        }

    # 2. Inject updated core tools into initrd (strictly mitra*)
    core_bin = REPO_ROOT / "core" / "bin"
    for tool_path in core_bin.glob("mitra*"):
        tool_bytes = tool_path.read_bytes()
        tname = tool_path.name
        for prefix in ["boot/apollo/", "bin/", "usr/bin/"]:
            entries[prefix + tname] = {
                'mode': 0o100755, 'uid': 0, 'gid': 0, 'nlink': 1,
                'mtime': int(time.time()), 'content': tool_bytes
            }

    # 2b. Inject Desktop UI & Framebuffer Assets
    mitra_share = REPO_ROOT / "rootfs" / "usr" / "share" / "mitraos"
    if mitra_share.exists():
        for asset in mitra_share.iterdir():
            if asset.is_file():
                asset_bytes = asset.read_bytes()
                for target_prefix in ["usr/share/mitraos/", "boot/mitraos/"]:
                    entries[target_prefix + asset.name] = {
                        'mode': 0o100644, 'uid': 0, 'gid': 0, 'nlink': 1,
                        'mtime': int(time.time()), 'content': asset_bytes
                    }
        print(f"[+] Injeksi aset visual desktop (/usr/share/mitraos)")

    # 2c. Inject Rootfs Configs (.jwmrc, system.jwmrc, xinitrc, xorg.conf)
    rootfs_dir = REPO_ROOT / "rootfs"
    for r_file in rootfs_dir.rglob("*"):
        if r_file.is_file():
            rel_path = r_file.relative_to(rootfs_dir).as_posix()
            entries[rel_path] = {
                'mode': 0o100755 if 'xinitrc' in rel_path or 'bin/' in rel_path else 0o100644,
                'uid': 0, 'gid': 0, 'nlink': 1,
                'mtime': int(time.time()),
                'content': r_file.read_bytes()
            }
    print(f"[+] Injeksi konfigurasi desktop rootfs (.jwmrc, xinitrc, xorg.conf)")

    # 3. Patch scripts/live inside initrd
    if "scripts/live" in entries:
        live_content = entries["scripts/live"]["content"].decode("utf-8", errors="ignore")
        
        # Inject CD-ROM runtime loader (x11_mitra_desktop.tar.gz and rootfs overlay)
        if "x11_mitra_desktop.tar.gz" not in live_content:
            target_marker = 'if [ -d "${rootmnt}/cdrom/mitraos" ]; then'
            if target_marker in live_content:
                x11_patch = '''		X11_PKG=$(find "${rootmnt}/cdrom" -iname "*x11*" 2>/dev/null | grep -E '\.(tar\.gz|tgz|gz)$' | head -n 1)
		if [ -n "$X11_PKG" ] && [ -f "$X11_PKG" ]; then
			echo "  [+] Memuat runtime desktop MitraOS ($X11_PKG)..."
			tar -xzf "$X11_PKG" -C "${rootmnt}/" 2>/dev/null || true
			chroot "${rootmnt}" ldconfig 2>/dev/null || true
		fi
		if [ -d "${rootmnt}/cdrom/rootfs" ]; then
			cp -rf "${rootmnt}/cdrom/rootfs/"* "${rootmnt}/" 2>/dev/null || true
		fi
'''
                live_content = live_content.replace(target_marker, x11_patch + target_marker)
                print("  [+] scripts/live X11 runtime loader hooked!")

        # Ensure essential device nodes exist in ${rootmnt}/dev for run-init and init
        if "mknod -m 600" not in live_content:
            cp_target = 'cp -a /bin /sbin /usr /lib* /etc /boot "${rootmnt}/" 2>/dev/null || true'
            dev_patch = '''cp -a /bin /sbin /usr /lib* /etc /boot "${rootmnt}/" 2>/dev/null || true
	mkdir -p "${rootmnt}/dev" 2>/dev/null || true
	cp -a /dev/* "${rootmnt}/dev/" 2>/dev/null || true
	mknod -m 600 "${rootmnt}/dev/console" c 5 1 2>/dev/null || true
	mknod -m 666 "${rootmnt}/dev/null" c 1 3 2>/dev/null || true
	mknod -m 666 "${rootmnt}/dev/zero" c 1 5 2>/dev/null || true
	mknod -m 666 "${rootmnt}/dev/ptmx" c 5 2 2>/dev/null || true
	mknod -m 666 "${rootmnt}/dev/tty" c 5 0 2>/dev/null || true
	mknod -m 620 "${rootmnt}/dev/tty1" c 4 1 2>/dev/null || true
	mknod -m 660 "${rootmnt}/dev/fb0" c 29 0 2>/dev/null || true
	mkdir -p "${rootmnt}/dev/input" 2>/dev/null || true
	mknod -m 666 "${rootmnt}/dev/input/mice" c 13 63 2>/dev/null || true
	mknod -m 666 "${rootmnt}/dev/input/mouse0" c 13 32 2>/dev/null || true'''
            if cp_target in live_content:
                live_content = live_content.replace(cp_target, dev_patch)
                print("  [+] scripts/live device nodes patch applied!")

        # Also ensure dev/console before run-init
        end_marker = 'chmod 755 "${rootmnt}/sbin/init"'
        if end_marker in live_content and 'mknod -m 600 "${rootmnt}/dev/console"' not in live_content:
            live_content = live_content.replace(end_marker, end_marker + '\n\tmknod -m 600 "${rootmnt}/dev/console" c 5 1 2>/dev/null || true\n\tcp -a /dev/* "${rootmnt}/dev/" 2>/dev/null || true')

        # Ensure PS1 prompt is mitra@apollo
        live_content = live_content.replace("mitra@mitraOS", "mitra@apollo")

        # Patch /sbin/init launch logic in scripts/live for Desktop mode
        desktop_marker = 'if grep -q -E \'gui=1|mitra_desktop|apollo_desktop\' /proc/cmdline 2>/dev/null; then'
        new_desktop_block = '''if grep -q -E 'gui=1|mitra_desktop|apollo_desktop' /proc/cmdline 2>/dev/null; then
	export MITRA_MODE="desktop"
	# Prepare dynamic input device symlinks for Xorg
	KB_DEV=$(grep -A 4 -i "keyboard" /proc/bus/input/devices 2>/dev/null | grep -o 'event[0-9]*' | head -n 1)
	[ -n "$KB_DEV" ] && ln -sf "/dev/input/$KB_DEV" /dev/input/hyperv_keyboard || ln -sf /dev/input/event0 /dev/input/hyperv_keyboard
	MOUSE_DEV=$(grep -A 4 -i "mouse" /proc/bus/input/devices 2>/dev/null | grep -o 'event[0-9]*' | head -n 1)
	[ -n "$MOUSE_DEV" ] && ln -sf "/dev/input/$MOUSE_DEV" /dev/input/hyperv_mouse || ln -sf /dev/input/event1 /dev/input/hyperv_mouse
	chmod 666 /dev/input/* 2>/dev/null || true
	mkdir -p /tmp/.X11-unix /var/log
	chmod 1777 /tmp/.X11-unix
	if [ -x /boot/apollo/mitra-desktop ]; then
		exec /boot/apollo/mitra-desktop --daemon
	elif [ -x /usr/bin/mitra-desktop ]; then
		exec /usr/bin/mitra-desktop --daemon
	fi
fi'''
        if desktop_marker in live_content:
            idx = live_content.find(desktop_marker)
            # find matching fi
            end_idx = live_content.find('\nfi\n', idx)
            if end_idx != -1:
                # also check inner fi
                inner_fi = live_content.find('\n\tfi\nfi', idx)
                if inner_fi != -1:
                    end_idx = inner_fi + 7
                else:
                    end_idx = end_idx + 4
                live_content = live_content[:idx] + new_desktop_block + live_content[end_idx:]
                print("  [+] scripts/live desktop launcher updated with input detection!")

        entries["scripts/live"]["content"] = live_content.encode("utf-8")

    # 4. Rebuild CPIO
    print("[*] Mengemas ulang arsip CPIO...")
    rebuilt_cpio = make_cpio(entries)
    print(f"[+] Ukuran CPIO baru: {len(rebuilt_cpio):,} bytes")

    # 5. Compress with zstandard (level 6)
    print("[*] Mengompresi initrd dengan Zstandard...")
    cctx = zstd.ZstdCompressor(level=6)
    compressed = cctx.compress(rebuilt_cpio)
    print(f"[+] Ukuran initrd terkompresi: {len(compressed):,} bytes")

    out_initrd = REPO_ROOT / "boot" / "kernel" / "initrd.img"
    with open(out_initrd, "wb") as f:
        f.write(compressed)
    
    # Also sync boot/initrd.img
    sync_initrd = REPO_ROOT / "boot" / "initrd.img"
    with open(sync_initrd, "wb") as f:
        f.write(compressed)
        
    print(f"[+] initrd berhasil diperbarui di kedua lokasi: {out_initrd} & {sync_initrd}")

if __name__ == "__main__":
    patch_initrd()
