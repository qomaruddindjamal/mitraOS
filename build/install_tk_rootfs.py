import urllib.request
import io
import tarfile
from pathlib import Path

repo_root = Path("c:/mitraOS")
rootfs = repo_root / "rootfs"

urls = [
    'http://deb.debian.org/debian/pool/main/t/tcl8.6/libtcl8.6_8.6.13+dfsg-2_amd64.deb',
    'http://deb.debian.org/debian/pool/main/t/tcl8.6/tcl8.6_8.6.13+dfsg-2_amd64.deb',
    'http://deb.debian.org/debian/pool/main/t/tk8.6/libtk8.6_8.6.13-2_amd64.deb',
    'http://deb.debian.org/debian/pool/main/t/tk8.6/tk8.6_8.6.13-2_amd64.deb',
    'http://deb.debian.org/debian/pool/main/libx/libxss/libxss1_1.2.3-1_amd64.deb'
]

print("[*] Mengunduh dan mengekstrak runtime Tk/Tcl ke dalam rootfs...")

for u in urls:
    print(f"  -> {u.split('/')[-1]} ...")
    req = urllib.request.Request(u, headers={'User-Agent': 'Wget/1.21.3'})
    deb_data = urllib.request.urlopen(req).read()
    
    pos = 8
    while pos < len(deb_data):
        hdr = deb_data[pos:pos+60]
        if len(hdr) < 60: break
        name = hdr[:16].decode('ascii', errors='ignore').strip()
        size = int(hdr[48:58].decode('ascii', errors='ignore').strip())
        content = deb_data[pos+60:pos+60+size]
        pos += 60 + size + (size % 2)
        if 'data.tar' in name:
            with tarfile.open(fileobj=io.BytesIO(content)) as tar_in:
                for m in tar_in.getmembers():
                    # Only install needed paths
                    if m.name.startswith(('./usr/bin', './usr/lib', './usr/share/tcltk')):
                        rel = m.name.lstrip('.').lstrip('/')
                        dest = rootfs / rel
                        if m.isdir():
                            dest.mkdir(parents=True, exist_ok=True)
                        elif m.isreg():
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            dest.write_bytes(tar_in.extractfile(m).read())
                        elif m.issym():
                            # create or store symlink
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            # On Windows, copy target file or write link
                            pass
            break

# Ensure symlinks /usr/bin/wish and /usr/bin/tclsh exist as copies on Windows
wish_bin = rootfs / "usr" / "bin" / "wish8.6"
if wish_bin.exists():
    (rootfs / "usr" / "bin" / "wish").write_bytes(wish_bin.read_bytes())
    print("[+] /usr/bin/wish terpasang.")

tclsh_bin = rootfs / "usr" / "bin" / "tclsh8.6"
if tclsh_bin.exists():
    (rootfs / "usr" / "bin" / "tclsh").write_bytes(tclsh_bin.read_bytes())
    print("[+] /usr/bin/tclsh terpasang.")

# Also symlink libtk8.6.so and libtcl8.6.so
lib_dir = rootfs / "usr" / "lib" / "x86_64-linux-gnu"
for libname in ["libtcl8.6.so", "libtk8.6.so", "libXss.so.1"]:
    for f in lib_dir.glob(f"{libname}*"):
        if f.is_file() and not (lib_dir / libname).exists():
            (lib_dir / libname).write_bytes(f.read_bytes())
            print(f"[+] {libname} terpasang.")

print("[+] Instalasi runtime Tk/Tcl ke rootfs selesai!")
