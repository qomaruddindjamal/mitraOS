#!/usr/bin/env python3
"""
MitraOS Initrd Patcher & Rebuilder (VHD Workstation Edition)
Integrates Native VHD Workstation Desktop (Xorg + JWM + Dock + Traffic Lights)
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

NEW_SCRIPTS_LIVE = '''# MitraOS Live Initramfs Hook
live_top()
{
	:
}

live_premount()
{
	:
}

live_bottom()
{
	:
}

mountroot()
{
	echo "MitraOS: Initializing Live Workstation System..." > /dev/console

	# Ensure busybox symlinks exist in initrd
	/bin/busybox --install -s /bin 2>/dev/null || true
	ln -sf /bin/busybox /bin/sh 2>/dev/null || true
	ln -sf /bin/busybox /bin/bash 2>/dev/null || true
	ln -sf /bin/busybox /bin/mount 2>/dev/null || true
	ln -sf /bin/busybox /bin/losetup 2>/dev/null || true
	ln -sf /bin/busybox /usr/bin/mount 2>/dev/null || true
	ln -sf /bin/busybox /usr/bin/losetup 2>/dev/null || true
	ln -sf /bin/busybox /usr/bin/sh 2>/dev/null || true

	# Ensure /lib/modules symlink exists in initrd
	[ ! -e /lib/modules ] && ln -sf /usr/lib/modules /lib/modules 2>/dev/null || true

	# Load storage & bus drivers
	modprobe isofs 2>/dev/null || true
	modprobe sr_mod 2>/dev/null || true
	modprobe cdrom 2>/dev/null || true
	modprobe loop 2>/dev/null || true
	modprobe ext4 2>/dev/null || true
	modprobe jbd2 2>/dev/null || true
	modprobe mbcache 2>/dev/null || true
	modprobe crc16 2>/dev/null || true
	modprobe scsi_mod 2>/dev/null || true
	modprobe sd_mod 2>/dev/null || true
	modprobe ata_piix 2>/dev/null || true
	modprobe virtio_blk 2>/dev/null || true
	modprobe hv_storvsc 2>/dev/null || true
	modprobe hv_vmbus 2>/dev/null || true
	modprobe hv_netvsc 2>/dev/null || true
	modprobe hyperv_fb 2>/dev/null || true
	modprobe fbcon 2>/dev/null || true
	modprobe evdev 2>/dev/null || true

	# Wait for CD-ROM / media to settle (up to 10s)
	CD_DEV=""
	for attempt in 1 2 3 4 5 6 7 8 9 10; do
		for dev in /dev/sr* /dev/cdrom /dev/sd* /dev/vd*; do
			[ -e "$dev" ] || continue
			mkdir -p /apollo_tmp
			if mount -r -t iso9660 "$dev" /apollo_tmp 2>/dev/null; then
				for img in \
					/apollo_tmp/mitraos/rootfs.img \
					/apollo_tmp/MITRAO/ROOTFS.IMG \
					/apollo_tmp/rootfs.img \
					/apollo_tmp/ROOTFS.IMG; do
					if [ -f "$img" ]; then
						CD_DEV="$dev"
						umount /apollo_tmp 2>/dev/null
						break 3
					fi
				done
				umount /apollo_tmp 2>/dev/null
			fi
		done
		sleep 1
	done

	# Mount dynamic writable tmpfs as root
	mount -t tmpfs -o size=800M tmpfs "${rootmnt}"

	mkdir -p "${rootmnt}/cdrom"
	if [ -n "$CD_DEV" ]; then
		mount -r -t iso9660 "$CD_DEV" "${rootmnt}/cdrom" 2>/dev/null || true
	fi

	ROOT_IMG=""
	for cand in \
		"${rootmnt}/cdrom/mitraos/rootfs.img" \
		"${rootmnt}/cdrom/MITRAO/ROOTFS.IMG" \
		"${rootmnt}/cdrom/rootfs.img" \
		"${rootmnt}/cdrom/ROOTFS.IMG" \
		"${rootmnt}/cdrom/apollo/rootfs.img"; do
		if [ -f "$cand" ]; then
			ROOT_IMG="$cand"
			break
		fi
	done

	VHD_MOUNTED=0
	if [ -n "$ROOT_IMG" ]; then
		echo "MitraOS: Mounting Workstation Rootfs from $ROOT_IMG..." > /dev/console
		mkdir -p "${rootmnt}/mnt/vhd"
		if /bin/busybox mount -r -t ext4 -o loop "$ROOT_IMG" "${rootmnt}/mnt/vhd" 2>/dev/console; then
			echo "MitraOS: Workstation Rootfs mounted successfully!" > /dev/console
			VHD_MOUNTED=1
			# Bind mount large read-only system directories (0 RAM used!)
			mkdir -p "${rootmnt}/usr" "${rootmnt}/lib" "${rootmnt}/lib64" "${rootmnt}/opt"
			/bin/busybox mount -o bind,ro "${rootmnt}/mnt/vhd/usr" "${rootmnt}/usr" 2>/dev/null || true
			/bin/busybox mount -o bind,ro "${rootmnt}/mnt/vhd/lib" "${rootmnt}/lib" 2>/dev/null || true
			/bin/busybox mount -o bind,ro "${rootmnt}/mnt/vhd/lib64" "${rootmnt}/lib64" 2>/dev/null || true
			/bin/busybox mount -o bind,ro "${rootmnt}/mnt/vhd/opt" "${rootmnt}/opt" 2>/dev/null || true

			# Copy small writable system directories into tmpfs root
			cp -a "${rootmnt}/mnt/vhd/bin" "${rootmnt}/" 2>/dev/null || true
			cp -a "${rootmnt}/mnt/vhd/sbin" "${rootmnt}/" 2>/dev/null || true
			cp -a "${rootmnt}/mnt/vhd/etc" "${rootmnt}/" 2>/dev/null || true
			cp -a "${rootmnt}/mnt/vhd/root" "${rootmnt}/" 2>/dev/null || true
			cp -a "${rootmnt}/mnt/vhd/var" "${rootmnt}/" 2>/dev/null || true
			cp -a "${rootmnt}/mnt/vhd/home" "${rootmnt}/" 2>/dev/null || true
		else
			echo "MitraOS: Warning: /bin/busybox mount failed on $ROOT_IMG" > /dev/console
		fi
	fi

	if [ "$VHD_MOUNTED" -eq 0 ]; then
		echo "MitraOS: Running in initramfs emergency fallback mode" > /dev/console
		mkdir -p "${rootmnt}/bin" "${rootmnt}/sbin" "${rootmnt}/usr/bin" "${rootmnt}/usr/sbin" \
		         "${rootmnt}/usr/lib" "${rootmnt}/lib" "${rootmnt}/lib64" "${rootmnt}/etc" \
		         "${rootmnt}/proc" "${rootmnt}/sys" "${rootmnt}/dev" "${rootmnt}/run" \
		         "${rootmnt}/tmp" "${rootmnt}/root" "${rootmnt}/boot/apollo/func" "${rootmnt}/cdrom" \
		         "${rootmnt}/home/apollo" "${rootmnt}/mnt" "${rootmnt}/var/log" "${rootmnt}/var/run"
		cp -a /bin /sbin /usr /lib* /etc /boot "${rootmnt}/" 2>/dev/null || true
	fi

	# Guarantee shell binaries exist in target root so run-init NEVER fails!
	mkdir -p "${rootmnt}/bin" "${rootmnt}/sbin"
	if [ ! -e "${rootmnt}/bin/sh" ]; then
		cp -a /bin/busybox "${rootmnt}/bin/busybox" 2>/dev/null || true
		ln -sf busybox "${rootmnt}/bin/sh" 2>/dev/null || true
	fi
	if [ ! -e "${rootmnt}/bin/bash" ]; then
		ln -sf /bin/sh "${rootmnt}/bin/bash" 2>/dev/null || true
	fi

	# Create standard virtual mount points
	mkdir -p "${rootmnt}/proc" "${rootmnt}/sys" "${rootmnt}/dev" "${rootmnt}/run" "${rootmnt}/tmp" "${rootmnt}/boot" "${rootmnt}/mnt"
	chmod 1777 "${rootmnt}/tmp" 2>/dev/null || true

	# Ensure modules & dynamic linker links exist
	if [ -d "${rootmnt}/usr/lib/modules" ] && [ ! -e "${rootmnt}/lib/modules" ]; then
		ln -sf /usr/lib/modules "${rootmnt}/lib/modules" 2>/dev/null || true
	fi
	mkdir -p "${rootmnt}/lib64" "${rootmnt}/usr/lib64" "${rootmnt}/lib" "${rootmnt}/usr/lib"
	if [ -f "${rootmnt}/lib64/ld-linux-x86-64.so.2" ]; then
		ln -sf /lib64/ld-linux-x86-64.so.2 "${rootmnt}/lib/ld-linux-x86-64.so.2" 2>/dev/null || true
		ln -sf /lib64/ld-linux-x86-64.so.2 "${rootmnt}/usr/lib/ld-linux-x86-64.so.2" 2>/dev/null || true
	elif [ -f "${rootmnt}/usr/lib/ld-linux-x86-64.so.2" ]; then
		ln -sf /usr/lib/ld-linux-x86-64.so.2 "${rootmnt}/lib64/ld-linux-x86-64.so.2" 2>/dev/null || true
		ln -sf /usr/lib/ld-linux-x86-64.so.2 "${rootmnt}/lib/ld-linux-x86-64.so.2" 2>/dev/null || true
	fi

	# Copy Mitra tools and modules from CD-ROM into PATH
	mkdir -p "${rootmnt}/boot/apollo" "${rootmnt}/boot/mitra"
	if [ -d "${rootmnt}/cdrom/mitraos/bin" ]; then
		cp -rf "${rootmnt}/cdrom/mitraos/bin/"* "${rootmnt}/boot/apollo/" 2>/dev/null || true
		cp -rf "${rootmnt}/cdrom/mitraos/bin/"* "${rootmnt}/bin/" 2>/dev/null || true
	fi
	if [ -d "${rootmnt}/cdrom/apollo/tools" ]; then
		cp -rf "${rootmnt}/cdrom/apollo/tools/"* "${rootmnt}/boot/apollo/" 2>/dev/null || true
	fi
	if [ -d "${rootmnt}/cdrom/apollo/func" ]; then
		mkdir -p "${rootmnt}/boot/apollo/func"
		cp -rf "${rootmnt}/cdrom/apollo/func/"* "${rootmnt}/boot/apollo/func/" 2>/dev/null || true
	fi
	if [ -d "${rootmnt}/cdrom/mitraos/lib" ]; then
		mkdir -p "${rootmnt}/opt/mitraos/lib"
		cp -rf "${rootmnt}/cdrom/mitraos/lib/"* "${rootmnt}/opt/mitraos/lib/" 2>/dev/null || true
	fi

	# Symlink all Mitra tools into /bin and /usr/bin
	rm -f "${rootmnt}/bin/apollo"* "${rootmnt}/usr/bin/apollo"* "${rootmnt}/boot/apollo/apollo"* 2>/dev/null || true
	for tool in "${rootmnt}/boot/apollo"/*; do
		[ -f "$tool" ] || continue
		btool="$(basename "$tool")"
		case "$btool" in
			apollo*) continue ;;
		esac
		ln -sf "/boot/apollo/$btool" "${rootmnt}/bin/$btool" 2>/dev/null || true
		ln -sf "/boot/apollo/$btool" "${rootmnt}/usr/bin/$btool" 2>/dev/null || true
		ln -sf "/boot/apollo/$btool" "${rootmnt}/boot/mitra/$btool" 2>/dev/null || true
	done

	# Set hostname to apollo (OS Codename)
	echo "apollo" > "${rootmnt}/etc/hostname"
	hostname "apollo" 2>/dev/null || true

	touch "${rootmnt}/etc/mitra_live" 2>/dev/null || true
	chmod -R 755 "${rootmnt}/boot/apollo" "${rootmnt}/boot/mitra" 2>/dev/null || true

	# Configure xinitrc
	mkdir -p "${rootmnt}/etc/X11/xinit"
	cat << 'EOF_XINIT' > "${rootmnt}/etc/X11/xinit/xinitrc"
#!/bin/sh
xsetroot -solid '#0a0e17' 2>/dev/null &
xset s off -dpms 2>/dev/null &
(sleep 0.5; feh --bg-fill /usr/share/mitraos/wallpaper.jpg 2>/dev/null || feh --bg-fill /usr/share/backgrounds/mitra-wallpaper.jpg 2>/dev/null) &
/usr/bin/mitra-dock-daemon &
while true; do
    jwm
    sleep 1
done
EOF_XINIT
	chmod 755 "${rootmnt}/etc/X11/xinit/xinitrc" 2>/dev/null || true

	# Set up profile
	cat << 'EOF_PROF' > "${rootmnt}/etc/profile"
export PATH="/boot/mitra:/boot/apollo:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME="/root"
export TERM="linux"
export USER="root"
export SHELL="/bin/bash"
export PS1='\\[\\033[01;36m\\]mitra\\[\\033[01;33m\\]@\\[\\033[01;32m\\]apollo\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]# '

alias ls='ls --color=auto'
alias ll='ls -la --color=auto'
alias banner='/boot/apollo/mitra-banner 0'
alias sysinfo='/boot/apollo/mitra-banner 0'
alias mitra='/boot/apollo/mitra'
alias apps='/boot/apollo/mitra-apps'
alias config='/boot/apollo/mitra-config'
alias asisten='/boot/apollo/mitra-asisten'
alias workstation='/usr/bin/workstation'

if [ -z "$MITRA_BANNER_SHOWN" ] && [ -t 1 ]; then
	export MITRA_BANNER_SHOWN=1
	if [ -x /usr/bin/mitra-banner ]; then
		/usr/bin/mitra-banner 0 2>/dev/null || true
	elif [ -x /boot/apollo/mitra-banner ]; then
		/boot/apollo/mitra-banner 0 2>/dev/null || true
	elif [ -x /bin/mitra-banner ]; then
		/bin/mitra-banner 0 2>/dev/null || true
	fi
fi
EOF_PROF

	cat << 'EOF_BASH' > "${rootmnt}/root/.bashrc"
[ -f /etc/profile ] && . /etc/profile
export PS1='\\[\\033[01;36m\\]mitra\\[\\033[01;33m\\]@\\[\\033[01;32m\\]apollo\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]# '
EOF_BASH
	cp "${rootmnt}/root/.bashrc" "${rootmnt}/root/.profile" 2>/dev/null || true

	# Generate /sbin/init for LiveCD
	cat << 'LAUNCHER' > "${rootmnt}/sbin/init"
#!/bin/sh
export PATH="/boot/mitra:/boot/apollo:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME="/root"
export TERM="linux"
export USER="root"
export SHELL="/bin/bash"
export PS1='\\[\\033[01;36m\\]mitra\\[\\033[01;33m\\]@\\[\\033[01;32m\\]apollo\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]# '
cd /root

mount -t proc proc /proc 2>/dev/null || true
mount -t sysfs sysfs /sys 2>/dev/null || true
mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
mount -t tmpfs tmpfs /run 2>/dev/null || true
mount -t tmpfs tmpfs /tmp 2>/dev/null || true
mkdir -p /dev/pts /dev/shm /var/run /var/log /etc/dropbear /root
mount -t devpts devpts /dev/pts 2>/dev/null || true
mount -t tmpfs tmpfs /dev/shm 2>/dev/null || true
chmod 1777 /tmp /dev/shm 2>/dev/null || true
chmod 700 /root /etc/dropbear 2>/dev/null || true

# Dynamic Hyper-V mouse & keyboard links
MOUSE_DEV=$(grep -A 4 "Microsoft Vmbus HID-compliant Mouse" /proc/bus/input/devices 2>/dev/null | grep -o 'event[0-9]*' | head -n 1)
if [ -n "$MOUSE_DEV" ] && [ -e "/dev/input/$MOUSE_DEV" ]; then
	ln -sf "/dev/input/$MOUSE_DEV" /dev/input/hyperv_mouse
else
	ln -sf /dev/input/event1 /dev/input/hyperv_mouse
fi

KBD_DEV=$(grep -A 4 "AT Translated Set 2 keyboard" /proc/bus/input/devices 2>/dev/null | grep -o 'event[0-9]*' | head -n 1)
if [ -n "$KBD_DEV" ] && [ -e "/dev/input/$KBD_DEV" ]; then
	ln -sf "/dev/input/$KBD_DEV" /dev/input/hyperv_keyboard
else
	ln -sf /dev/input/event0 /dev/input/hyperv_keyboard
fi
chmod 666 /dev/input/* 2>/dev/null || true

# Network Drivers & Interface Setup
modprobe hv_vmbus 2>/dev/null || true
modprobe hv_netvsc 2>/dev/null || true
modprobe virtio_net 2>/dev/null || true
modprobe e1000 2>/dev/null || true
modprobe e1000e 2>/dev/null || true
modprobe r8169 2>/dev/null || true

ip link set lo up 2>/dev/null || true
for iface in $(ip -o link show 2>/dev/null | awk -F': ' '{print $2}' | grep -v '^lo$'); do
	ip link set "$iface" up 2>/dev/null || true
	udhcpc -i "$iface" -n -q -t 3 -b 2>/dev/null &
done

# Dropbear SSH daemon
if ! pidof dropbear >/dev/null 2>&1; then
	[ -x /usr/sbin/dropbear ] && /usr/sbin/dropbear -R -B -p 22 2>/dev/null &
fi

# Desktop Environment / GUI Edition boot mode (Native Xorg + JWM + macOS Style Workstation)
if grep -q -E 'gui=1|mitra_desktop|apollo_desktop' /proc/cmdline 2>/dev/null; then
	export MITRA_MODE="desktop"
	# Early bootsplash
	if [ -f /usr/share/mitraos/bootframes/frame_00.raw ] && [ -c /dev/fb0 ]; then
		cat /usr/share/mitraos/bootframes/frame_00.raw > /dev/fb0 2>/dev/null || true
	fi
	if [ -x /usr/bin/mitra-bootsplash ]; then
		/usr/bin/mitra-bootsplash 2>/dev/null || true
	fi

	export DISPLAY=:0
	touch /root/.Xauthority 2>/dev/null || true
	chmod 600 /root/.Xauthority 2>/dev/null || true
	chmod 755 /etc/X11/xinit/xinitrc 2>/dev/null || true
	# Supervised Xorg + JWM Workstation loop
	while true; do
		if [ -x /usr/bin/xinit ] && [ -x /usr/lib/xorg/Xorg ]; then
			/usr/bin/xinit /etc/X11/xinit/xinitrc -- /usr/lib/xorg/Xorg :0 vt1 >/var/log/xorg_session.log 2>&1
		elif [ -x /boot/apollo/mitra-desktop ]; then
			/boot/apollo/mitra-desktop --daemon
		elif [ -x /usr/bin/mitra-desktop ]; then
			/usr/bin/mitra-desktop --daemon
		fi
		sleep 1
	done
fi

# Console Workstation (CLI & Installer) mode
export MITRA_MODE="cli"
clear
if [ -x /boot/apollo/mitra-banner ]; then
	/boot/apollo/mitra-banner 0 2>/dev/null || true
elif [ -x /usr/local/bin/mitra-banner ]; then
	/usr/local/bin/mitra-banner 0 2>/dev/null || true
elif [ -x /bin/mitra-banner ]; then
	/bin/mitra-banner 0 2>/dev/null || true
fi

while true; do
	if [ -x /bin/busybox ]; then
		/bin/busybox setsid /bin/busybox cttyhack /bin/bash --login < /dev/tty1 > /dev/tty1 2>&1
	else
		/bin/bash --login < /dev/tty1 > /dev/tty1 2>&1
	fi
	sleep 1
done
LAUNCHER
	chmod 755 "${rootmnt}/sbin/init"

	log_end_msg
}
'''

def patch_initrd():
    print("[*] Membaca arsip initrd base...")
    cpio_path = REPO_ROOT / "build" / "initrd.cpio"
    with open(cpio_path, "rb") as f:
        entries = parse_cpio(f.read())
    print(f"[+] Total {len(entries)} entri terbaca dari initrd cpio.")

    # 0. Purge heavy/redundant items from initrd to save RAM:
    # cloudflared (38MB), large raw frames, extra EFI files
    # These are already in rootfs.ext4!
    removed = 0
    for k in list(entries.keys()):
        if any(k.startswith(p) for p in [
            "bin/apollo", "usr/bin/apollo", "sbin/apollo", "boot/apollo/apollo",
            "usr/bin/cloudflared", "boot/efi/EFI/BOOT/BOOTX64.EFI", "boot/apollo/BOOTX64.EFI"
        ]):
            if k == "boot/apollo/func/apollo-globals":
                continue
            del entries[k]
            removed += 1
        elif k.endswith(".raw"):
            del entries[k]
            removed += 1
    print(f"[+] Dihapus {removed} entri berat/redundant dari initrd untuk hemat RAM.")

    # Add /lib/modules symlink to /usr/lib/modules so modprobe works in initramfs
    entries["lib/modules"] = {
        'mode': 0o120777, 'uid': 0, 'gid': 0, 'nlink': 1,
        'mtime': int(time.time()), 'content': b'../usr/lib/modules'
    }

    # Ensure busybox handles mount, losetup, sh in initramfs
    for p, target in [
        ("bin/sh", b'busybox'),
        ("bin/bash", b'busybox'),
        ("bin/mount", b'busybox'),
        ("bin/losetup", b'busybox'),
        ("usr/bin/mount", b'../../bin/busybox'),
        ("usr/bin/losetup", b'../../bin/busybox'),
        ("usr/bin/sh", b'../../bin/busybox'),
    ]:
        entries[p] = {
            'mode': 0o120777, 'uid': 0, 'gid': 0, 'nlink': 1,
            'mtime': int(time.time()), 'content': target
        }

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
        "bin/mitra-globals",
        "usr/bin/mitra-globals"
    ]:
        entries[path] = {
            'mode': 0o100755, 'uid': 0, 'gid': 0, 'nlink': 1,
            'mtime': int(time.time()), 'content': globals_bytes
        }

    # 2. Update scripts/live with native VHD loop loader
    entries["scripts/live"] = {
        'mode': 0o100755, 'uid': 0, 'gid': 0, 'nlink': 1,
        'mtime': int(time.time()), 'content': NEW_SCRIPTS_LIVE.encode('utf-8')
    }
    print("  [+] scripts/live updated with lightweight VHD loop loader!")

    # 3. Rebuild CPIO
    print("[*] Mengemas ulang arsip CPIO...")
    rebuilt_cpio = make_cpio(entries)
    print(f"[+] Ukuran CPIO baru: {len(rebuilt_cpio):,} bytes ({len(rebuilt_cpio)/(1024*1024):.1f} MB)")

    # 4. Compress with zstandard (level 6)
    print("[*] Mengompresi initrd dengan Zstandard...")
    cctx = zstd.ZstdCompressor(level=6)
    compressed = cctx.compress(rebuilt_cpio)
    print(f"[+] Ukuran initrd terkompresi: {len(compressed):,} bytes ({len(compressed)/(1024*1024):.1f} MB)")

    out_initrd = REPO_ROOT / "boot" / "kernel" / "initrd.img"
    with open(out_initrd, "wb") as f:
        f.write(compressed)
    print(f"[+] initrd berhasil diperbarui: {out_initrd}")

if __name__ == "__main__":
    patch_initrd()
