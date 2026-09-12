import paramiko
import time

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('172.23.101.33', 22, 'root', 'admin123')

script = """#!/bin/bash
set -e
echo "[*] Initializing loop device..."
modprobe loop 2>/dev/null || true

echo "[*] Creating /rootfs.ext4 (1400MB)..."
rm -f /rootfs.ext4
truncate -s 1400M /rootfs.ext4
mke2fs -F -b 4096 -m 0 -L MITRA_ROOT /rootfs.ext4

mkdir -p /mnt/live_rootfs
losetup /dev/loop0 /rootfs.ext4
mount /dev/loop0 /mnt/live_rootfs

echo "[*] Copying system directories..."
cp -a /bin /etc /home /lib /lib64 /opt /root /sbin /usr /var /mnt/live_rootfs/
mkdir -p /mnt/live_rootfs/proc /mnt/live_rootfs/sys /mnt/live_rootfs/dev /mnt/live_rootfs/run /mnt/live_rootfs/tmp /mnt/live_rootfs/boot /mnt/live_rootfs/cdrom /mnt/live_rootfs/mnt
chmod 1777 /mnt/live_rootfs/tmp

echo "[*] Cleaning and customizing rootfs..."
rm -f /mnt/live_rootfs/swapfile /mnt/live_rootfs/*.tar.gz 2>/dev/null || true
rm -f /mnt/live_rootfs/bin/apollo* /mnt/live_rootfs/usr/bin/apollo* /mnt/live_rootfs/boot/apollo/apollo* 2>/dev/null || true

# Set hostname to apollo
echo "apollo" > /mnt/live_rootfs/etc/hostname
cat << 'EOF_HOSTS' > /mnt/live_rootfs/etc/hosts
127.0.0.1\tlocalhost
127.0.1.1\tapollo
::1\t\tlocalhost ip6-localhost ip6-loopback
EOF_HOSTS

# Set prompt to mitra@apollo
sed -i 's/mitra@citramedia/mitra@apollo/g' /mnt/live_rootfs/etc/profile /mnt/live_rootfs/root/.bashrc 2>/dev/null || true
sed -i 's/mitra@mitraOS/mitra@apollo/g' /mnt/live_rootfs/etc/profile /mnt/live_rootfs/root/.bashrc 2>/dev/null || true

# Update /sbin/init to support both Live GUI & Live CLI
cat << 'EOF_INIT' > /mnt/live_rootfs/sbin/init
#!/bin/bash
export PATH="/boot/mitra:/boot/apollo:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME="/root"
export TERM="linux"
export SHELL="/bin/bash"

# Mount virtual filesystems
mount -t proc proc /proc 2>/dev/null || true
mount -t sysfs sysfs /sys 2>/dev/null || true
mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
mount -t tmpfs tmpfs /run 2>/dev/null || true
mount -t tmpfs tmpfs /tmp 2>/dev/null || true
mkdir -p /dev/pts /dev/shm
mount -t devpts devpts /dev/pts 2>/dev/null || true
mount -t tmpfs tmpfs /dev/shm 2>/dev/null || true

# Early bootsplash frame on GUI boot to mask console immediately
if grep -q -E "gui=1|mitra_desktop|apollo_desktop" /proc/cmdline; then
    echo 0 > /sys/class/graphics/fbcon/cursor_blink 2>/dev/null
    setterm -cursor off > /dev/tty1 2>/dev/null || true
    if [ -f /usr/share/mitraos/bootframes/frame_00.raw ]; then
        cat /usr/share/mitraos/bootframes/frame_00.raw > /dev/fb0 2>/dev/null
    fi
fi

[ -f /etc/hostname ] && hostname -F /etc/hostname 2>/dev/null || hostname apollo 2>/dev/null || true

[ -d /usr/lib/modules ] && [ ! -e /lib/modules ] && ln -sf /usr/lib/modules /lib/modules 2>/dev/null || true
modprobe ext4 2>/dev/null || true
modprobe hv_vmbus 2>/dev/null || true
modprobe hv_netvsc 2>/dev/null || true
modprobe hyperv_keyboard 2>/dev/null || true
modprobe hid_hyperv 2>/dev/null || true

# Load input and filesystem modules
for m in /lib/modules/6.1.0-52-amd64/kernel/drivers/input/*.ko; do
    [ -f "$m" ] && insmod "$m" 2>/dev/null || true
done
for m in /boot/apollo/modules/*.ko; do
    [ -f "$m" ] && insmod "$m" 2>/dev/null || true
done
chmod 666 /dev/input/* 2>/dev/null || true

# Dynamic Hyper-V absolute mouse event device link
MOUSE_DEV=$(grep -A 4 "Microsoft Vmbus HID-compliant Mouse" /proc/bus/input/devices 2>/dev/null | grep -o 'event[0-9]*' | head -n 1)
if [ -n "$MOUSE_DEV" ] && [ -e "/dev/input/$MOUSE_DEV" ]; then
    ln -sf "/dev/input/$MOUSE_DEV" /dev/input/hyperv_mouse
else
    ln -sf /dev/input/event1 /dev/input/hyperv_mouse
fi

# Dynamic Hyper-V keyboard event device link
KBD_DEV=$(grep -A 4 "AT Translated Set 2 keyboard" /proc/bus/input/devices 2>/dev/null | grep -o 'event[0-9]*' | head -n 1)
if [ -n "$KBD_DEV" ] && [ -e "/dev/input/$KBD_DEV" ]; then
    ln -sf "/dev/input/$KBD_DEV" /dev/input/hyperv_keyboard
else
    ln -sf /dev/input/event0 /dev/input/hyperv_keyboard
fi

ip link set lo up 2>/dev/null || true
ip link set eth0 up 2>/dev/null || true
udhcpc -i eth0 -n -q -s /usr/share/udhcpc/default.script 2>/dev/null || udhcpc -i eth0 -n -q 2>/dev/null || true
echo "nameserver 1.1.1.1" > /etc/resolv.conf 2>/dev/null || true
echo "nameserver 8.8.8.8" >> /etc/resolv.conf 2>/dev/null || true

mkdir -p /etc/dropbear
chmod 700 /etc/dropbear 2>/dev/null || true
chmod 600 /etc/dropbear/* 2>/dev/null || true
if ! pidof dropbear >/dev/null 2>&1; then
    [ -x /usr/sbin/dropbear ] && /usr/sbin/dropbear -R -B -p 22 2>/dev/null &
fi

# Ensure /boot/mitra symlink exists
[ ! -d /boot/mitra ] && ln -sf /boot/apollo /boot/mitra 2>/dev/null || true

if grep -q -E "gui=1|mitra_desktop|apollo_desktop" /proc/cmdline; then
    # Play macOS-Style Animated Bootsplash Progress Animation
    if [ -x /usr/bin/mitra-bootsplash ]; then
        /usr/bin/mitra-bootsplash
    fi
    export DISPLAY=:0
    # Supervised loop: PID 1 MUST NEVER DIE!
    while true; do
        /usr/bin/xinit /etc/X11/xinit/xinitrc -- /usr/lib/xorg/Xorg :0 vt1 -auth /root/.Xauthority >/var/log/xorg_session.log 2>&1
        sleep 1
    done
fi

clear
if [ -x /boot/apollo/mitra-banner ]; then
    /boot/apollo/mitra-banner 0 2>/dev/null || true
elif [ -x /usr/local/bin/mitra-banner ]; then
    /usr/local/bin/mitra-banner 0 2>/dev/null || true
elif [ -x /bin/mitra-banner ]; then
    /bin/mitra-banner 0 2>/dev/null || true
fi

while true; do
    /bin/busybox setsid /bin/busybox cttyhack /bin/bash --login < /dev/tty1 > /dev/tty1 2>&1
    sleep 1
done
EOF_INIT
chmod 755 /mnt/live_rootfs/sbin/init

echo "[*] Checking filesystem size on /mnt/live_rootfs:"
df -h /mnt/live_rootfs

umount /mnt/live_rootfs
losetup -d /dev/loop0
rmdir /mnt/live_rootfs
echo "[+] /rootfs.ext4 successfully created and ready!"
ls -lh /rootfs.ext4
"""

stdin, stdout, stderr = s.exec_command(f"cat << 'EOS' > /tmp/make_img.sh\n{script}\nEOS\nbash /tmp/make_img.sh")
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("Errors/Warnings:\n", err)

s.close()
