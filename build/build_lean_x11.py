#!/usr/bin/env python3
import tarfile
import struct
import io
import os
from pathlib import PurePosixPath, Path

def get_needed(data):
    if len(data) < 64 or data[:4] != b'\x7fELF':
        return []
    is_64 = data[4] == 2
    is_le = data[5] == 1
    endian = '<' if is_le else '>'
    
    if is_64:
        e_shoff = struct.unpack_from(endian + 'Q', data, 40)[0]
        e_shentsize = struct.unpack_from(endian + 'H', data, 58)[0]
        e_shnum = struct.unpack_from(endian + 'H', data, 60)[0]
        
        sections = []
        for i in range(e_shnum):
            off = e_shoff + i * e_shentsize
            sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link = struct.unpack_from(endian + 'IIQQQQI', data, off)
            sections.append({
                'type': sh_type, 'offset': sh_offset, 'size': sh_size, 'link': sh_link
            })
            
        dyn_sec = next((s for s in sections if s['type'] == 6), None)
        if not dyn_sec:
            return []
        str_sec = sections[dyn_sec['link']]
        strtab = data[str_sec['offset']:str_sec['offset'] + str_sec['size']]
        
        needed = []
        off = dyn_sec['offset']
        while off < dyn_sec['offset'] + dyn_sec['size']:
            d_tag, d_val = struct.unpack_from(endian + 'qQ', data, off)
            if d_tag == 0:
                break
            if d_tag == 1: # DT_NEEDED
                name_end = strtab.find(b'\0', d_val)
                needed.append(strtab[d_val:name_end].decode('ascii', errors='ignore'))
            off += 16
        return needed
    return []

def main():
    print("[*] Mengindeks arsip sumber X11 dan input drivers...")
    files_map = {}
    for tpath in [Path('C:/mitraOS_/x11_mitra_desktop.tar.gz'), Path('C:/mitraOS_/input_drivers.tar.gz')]:
        if tpath.exists():
            print(f"  -> Membaca {tpath}...")
            with tarfile.open(tpath, 'r:gz') as tar:
                for m in tar.getmembers():
                    norm_name = m.name.replace('\\', '/').strip('/')
                    if m.isreg():
                        files_map[norm_name] = (m, tar.extractfile(m).read())
                    elif m.issym() or m.islnk():
                        files_map[norm_name] = (m, b'')

    # Map basename to list of candidate full paths
    so_map = {}
    for name in files_map:
        b = PurePosixPath(name).name
        so_map.setdefault(b, []).append(name)

    def resolve_symlink(name):
        visited = set()
        curr = name
        chain = [curr]
        while curr in files_map:
            m, data = files_map[curr]
            if m.isreg():
                return curr, data, chain
            if m.issym() or m.islnk():
                visited.add(curr)
                link_target = m.linkname.replace('\\', '/').strip('/')
                p = PurePosixPath(curr).parent / link_target
                parts = []
                for part in str(p).split('/'):
                    if part == '..':
                        if parts: parts.pop()
                    elif part and part != '.':
                        parts.append(part)
                curr = '/'.join(parts)
                chain.append(curr)
                if curr in visited:
                    break
            else:
                break
        return None, b'', chain

    seeds = [
        'usr/lib/xorg/Xorg', 'usr/bin/Xorg', 'usr/bin/xinit', 'usr/bin/jwm', 'usr/bin/xterm',
        'usr/bin/feh', 'usr/bin/xsetroot', 'usr/bin/setxkbmap', 'usr/bin/xkbcomp', 'usr/bin/xauth',
        'usr/bin/xrdb', 'usr/bin/xset', 'usr/bin/xrandr', 'usr/bin/xmodmap',
        'usr/lib/xorg/modules/drivers/fbdev_drv.so',
        'usr/lib/xorg/modules/drivers/modesetting_drv.so',
        'usr/lib/xorg/modules/input/kbd_drv.so',
        'usr/lib/xorg/modules/input/mouse_drv.so',
        'usr/lib/xorg/modules/input/evdev_drv.so',
        'usr/lib/xorg/modules/libwfb.so',
        'usr/lib/xorg/modules/libshadow.so',
        'usr/lib/xorg/modules/libshadowfb.so',
        'usr/lib/xorg/modules/libfbdevhw.so',
        'usr/lib/xorg/modules/libglx.so',
        'usr/lib/xorg/modules/libexa.so',
        'usr/lib/x86_64-linux-gnu/libevdev.so.2',
        'usr/lib/x86_64-linux-gnu/libmtdev.so.1'
    ]

    required_files = set()
    queue = list(seeds)

    print("[*] Melakukan analisis penutupan dependensi (dependency closure)...")
    while queue:
        curr = queue.pop(0)
        if curr in required_files or curr not in files_map:
            continue
        required_files.add(curr)
        
        m, data = files_map[curr]
        if m.issym() or m.islnk():
            real_target, real_data, chain = resolve_symlink(curr)
            for link_elem in chain:
                if link_elem in files_map and link_elem not in required_files:
                    required_files.add(link_elem)
            data = real_data
        
        for lib in get_needed(data):
            candidates = so_map.get(lib, [])
            if not candidates:
                for b in so_map:
                    if b.startswith(lib):
                        candidates.extend(so_map[b])
            for c in candidates:
                if c not in required_files:
                    queue.append(c)

    # Extra directories: xkb, fonts, locales, terminfo
    extra_prefixes = [
        'etc/X11', 'etc/jwm', 'usr/share/X11/xkb', 'usr/share/fonts',
        'usr/share/X11/locale', 'usr/share/terminfo', 'lib/terminfo'
    ]

    for name in files_map:
        if any(name.startswith(p) for p in extra_prefixes):
            if not any(name.endswith(ext) for ext in ['.txt', '.html', '.md', '.doc', '.man', '.h']):
                required_files.add(name)

    # Ensure every symlink has its target included, or skip broken ones
    valid_files = set()
    for name in required_files:
        m, data = files_map[name]
        if m.issym() or m.islnk():
            real_target, _, chain = resolve_symlink(name)
            if real_target:
                valid_files.add(name)
                for link_elem in chain:
                    if link_elem in files_map:
                        valid_files.add(link_elem)
        else:
            valid_files.add(name)

    out_pkg = Path('packages/x11_mitra_desktop.tar.gz')
    out_pkg.parent.mkdir(parents=True, exist_ok=True)
    print(f"[*] Mengemas {len(valid_files)} file valid ke {out_pkg}...")

    with tarfile.open(out_pkg, 'w:gz') as tar:
        for name in sorted(valid_files):
            m, data = files_map[name]
            ti = tarfile.TarInfo(name=name)
            
            # Set proper executable permissions
            if any(x in name for x in ['bin/', 'sbin/', 'Xorg', 'xkbcomp']) or name.endswith('.so') or '.so.' in name:
                ti.mode = 0o755
            else:
                ti.mode = 0o644
                
            ti.uid = 0
            ti.gid = 0
            ti.mtime = m.mtime
            ti.type = m.type
            
            if m.issym() or m.islnk():
                ti.linkname = m.linkname.replace('\\', '/')
                tar.addfile(ti)
            elif m.isreg():
                ti.size = len(data)
                tar.addfile(ti, io.BytesIO(data))
            else:
                tar.addfile(ti)

    print(f"[+] Selesai! Ukuran paket terkompresi: {out_pkg.stat().st_size / (1024*1024):.2f} MB")

if __name__ == '__main__':
    main()
