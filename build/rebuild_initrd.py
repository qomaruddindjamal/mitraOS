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

    # Injeksi hostname & hosts (Apollo sebagai Kode OS v1)
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

    # 3. Patch scripts/live inside initrd
    if "scripts/live" in entries:
        live_content = entries["scripts/live"]["content"].decode("utf-8", errors="ignore")
        
        orig_tools = '''		if [ -d "${rootmnt}/cdrom/apollo/tools" ]; then
			cp -rf "${rootmnt}/cdrom/apollo/tools/"* "${rootmnt}/boot/apollo/" 2>/dev/null || true
		fi'''

        new_tools = '''		if [ -d "${rootmnt}/cdrom/apollo/tools" ]; then
			cp -rf "${rootmnt}/cdrom/apollo/tools/"* "${rootmnt}/boot/apollo/" 2>/dev/null || true
		fi
		if [ -d "${rootmnt}/cdrom/apollo/func" ]; then
			mkdir -p "${rootmnt}/boot/apollo/func" 2>/dev/null || true
			cp -rf "${rootmnt}/cdrom/apollo/func/"* "${rootmnt}/boot/apollo/func/" 2>/dev/null || true
		fi
		if [ -d "${rootmnt}/cdrom/mitraos" ]; then
			mkdir -p "${rootmnt}/opt/mitraos" "${rootmnt}/boot/mitraos" "${rootmnt}/usr/share/mitraos" 2>/dev/null || true
			cp -rf "${rootmnt}/cdrom/mitraos/"* "${rootmnt}/opt/mitraos/" 2>/dev/null || true
			cp -rf "${rootmnt}/cdrom/mitraos/"* "${rootmnt}/boot/mitraos/" 2>/dev/null || true
		fi
		if [ -d "${rootmnt}/cdrom/rootfs/usr/share/mitraos" ]; then
			mkdir -p "${rootmnt}/usr/share/mitraos" 2>/dev/null || true
			cp -rf "${rootmnt}/cdrom/rootfs/usr/share/mitraos/"* "${rootmnt}/usr/share/mitraos/" 2>/dev/null || true
		fi'''

        if orig_tools in live_content:
            live_content = live_content.replace(orig_tools, new_tools)
            print("  [+] scripts/live CD-ROM loader patched!")

        # Ensure PS1 prompt is mitra@apollo
        live_content = live_content.replace("mitra@mitraOS", "mitra@apollo")

        # Hook tool symlinker to purge apollo commands and set hostname
        symlink_orig = '''for tool in "${rootmnt}/boot/apollo"/*; do
		[ -f "$tool" ] || continue
		btool="$(basename "$tool")"'''
        symlink_hooked = '''# Purge any legacy apollo executables
	rm -f "${rootmnt}/bin/apollo"* "${rootmnt}/usr/bin/apollo"* "${rootmnt}/boot/apollo/apollo"* 2>/dev/null || true

	# Set system hostname to apollo (OS Codename)
	echo "apollo" > "${rootmnt}/etc/hostname"
	hostname "apollo" 2>/dev/null || true

	# Symlink all Mitra tools from /boot/apollo to /bin and /usr/bin without duplication
	for tool in "${rootmnt}/boot/apollo"/*; do
		[ -f "$tool" ] || continue
		btool="$(basename "$tool")"
		case "$btool" in
			apollo*) continue ;; # Skip legacy apollo commands
		esac'''

        if symlink_orig in live_content:
            live_content = live_content.replace(symlink_orig, symlink_hooked)
            print("  [+] scripts/live tool symlinker and apollo purge hooked!")

        # Patch /sbin/init launch logic in scripts/live
        init_exec_orig = '''# Launch interactive login shell with controlling terminal
# Banner will be cleanly displayed once via /etc/profile
if [ -x /bin/busybox ]; then
	exec /bin/busybox setsid /bin/busybox cttyhack /bin/bash --login
else
	exec /bin/bash --login
fi'''

        init_exec_patched = '''# Desktop Environment / GUI Edition boot mode
if grep -q -E 'gui=1|mitra_desktop|apollo_desktop' /proc/cmdline 2>/dev/null; then
	export MITRA_MODE="desktop"
	if [ -x /boot/apollo/mitra-desktop ]; then
		if [ -x /bin/busybox ]; then
			exec /bin/busybox setsid /bin/busybox cttyhack /boot/apollo/mitra-desktop --daemon
		else
			exec /boot/apollo/mitra-desktop --daemon
		fi
	elif [ -x /usr/bin/mitra-desktop ]; then
		if [ -x /bin/busybox ]; then
			exec /bin/busybox setsid /bin/busybox cttyhack /usr/bin/mitra-desktop --daemon
		else
			exec /usr/bin/mitra-desktop --daemon
		fi
	fi
fi

# Console Workstation (CLI & Installer) mode
export MITRA_MODE="cli"
if [ -x /bin/busybox ]; then
	exec /bin/busybox setsid /bin/busybox cttyhack /bin/bash --login
else
	exec /bin/bash --login
fi'''

        if init_exec_orig in live_content:
            live_content = live_content.replace(init_exec_orig, init_exec_patched)
            print("  [+] scripts/live init launcher patched for Desktop mode!")

        # Ensure /etc/profile only prints banner when in CLI mode
        profile_banner_orig = '''# Display MitraOS Banner on login
if [ -z "$MITRA_BANNER_SHOWN" ] && [ -t 1 ]; then
	export MITRA_BANNER_SHOWN=1
	if [ -x /boot/apollo/mitra-banner ]; then
		/boot/apollo/mitra-banner 0
	elif [ -x /bin/mitra-banner ]; then
		/bin/mitra-banner 0
	fi
fi'''

        profile_banner_patched = '''# Display MitraOS Banner on login
if [ "$MITRA_MODE" != "desktop" ] && [ -z "$MITRA_BANNER_SHOWN" ] && [ -t 1 ]; then
	export MITRA_BANNER_SHOWN=1
	if [ -x /boot/apollo/mitra-banner ]; then
		/boot/apollo/mitra-banner 0
	elif [ -x /bin/mitra-banner ]; then
		/bin/mitra-banner 0
	fi
fi'''
        if profile_banner_orig in live_content:
            live_content = live_content.replace(profile_banner_orig, profile_banner_patched)
            print("  [+] scripts/live /etc/profile banner conditionalized!")

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
    print(f"[+] initrd berhasil diperbarui: {out_initrd}")

if __name__ == "__main__":
    patch_initrd()
