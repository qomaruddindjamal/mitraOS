from pathlib import Path

repo_root = Path("c:/mitraOS")

files = [
    repo_root / "rootfs" / "root" / ".jwmrc",
    repo_root / "rootfs" / "etc" / "jwm" / "system.jwmrc"
]

for fpath in files:
    raw = fpath.read_bytes()
    # 1. Dock button: direct execution of dispatcher (launches native GUI without terminal)
    raw = raw.replace(
        b'popup="System Preferences">exec:/usr/bin/mitra-terminal -e /usr/bin/mitra-preferences</TrayButton>',
        b'popup="System Preferences">exec:/usr/bin/mitra-preferences</TrayButton>'
    )
    # 2. Menu items: direct execution of dispatcher
    raw = raw.replace(
        b'label="System Preferences">/usr/bin/mitra-terminal -e /usr/bin/mitra-preferences</Program>',
        b'label="System Preferences">/usr/bin/mitra-preferences</Program>'
    )
    fpath.write_bytes(raw)
    print(f"[+] Updated {fpath} to call /usr/bin/mitra-preferences directly")
