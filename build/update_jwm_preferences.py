from pathlib import Path

repo_root = Path("c:/mitraOS")

files = [
    repo_root / "rootfs" / "root" / ".jwmrc",
    repo_root / "rootfs" / "etc" / "jwm" / "system.jwmrc"
]

for fpath in files:
    raw = fpath.read_bytes()
    # 1. Replace dock button
    raw = raw.replace(
        b'popup="System Preferences">exec:/usr/bin/mitra-preferences</TrayButton>',
        b'popup="System Preferences">exec:/usr/bin/mitra-terminal -e /usr/bin/mitra-preferences</TrayButton>'
    )
    # 2. Replace menu items
    raw = raw.replace(
        b'label="System Preferences">/usr/bin/mitra-preferences</Program>',
        b'label="System Preferences">/usr/bin/mitra-terminal -e /usr/bin/mitra-preferences</Program>'
    )
    # 3. Add to Menu b (Workstation) if not present
    if b'label="System Preferences"' not in raw.split(b'<RootMenu onroot="b">')[1].split(b'</RootMenu>')[0]:
        target = b'<Program label="Control Center">/usr/bin/mitra-terminal -e /boot/apollo/mitra</Program>'
        replacement = target + b'\r\n        <Program icon="/usr/share/mitraos/icons/system-preferences/preferences-system.png" label="System Preferences">/usr/bin/mitra-terminal -e /usr/bin/mitra-preferences</Program>' if b'\r\n' in raw else target + b'\n        <Program icon="/usr/share/mitraos/icons/system-preferences/preferences-system.png" label="System Preferences">/usr/bin/mitra-terminal -e /usr/bin/mitra-preferences</Program>'
        raw = raw.replace(target, replacement, 1)

    fpath.write_bytes(raw)
    print(f"Successfully patched {fpath}")
