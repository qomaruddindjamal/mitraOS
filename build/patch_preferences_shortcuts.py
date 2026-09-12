from pathlib import Path

repo_root = Path("c:/mitraOS")

files = [
    repo_root / "rootfs" / "usr" / "bin" / "mitra-preferences",
    repo_root / "core" / "bin" / "mitra-preferences",
    repo_root / "rootfs" / "opt" / "mitraos" / "bin" / "mitra-preferences"
]

for fpath in files:
    if fpath.exists():
        raw = fpath.read_bytes()
        # Convert any CRLF to LF
        raw = raw.replace(b"\r\n", b"\n")
        
        # Make CHOICE exit flexible
        raw = raw.replace(
            b'[[ -z "$CHOICE" || "$CHOICE" == "X" ]] && break',
            b'[[ -z "$CHOICE" || "$CHOICE" =~ ^[Xx0Qq]$ ]] && break'
        )
        
        # Make submenu back flexible
        raw = raw.replace(
            b'[[ -z "$sel" || "$sel" == "B" ]] && break',
            b'[[ -z "$sel" || "$sel" =~ ^[Bb0XxQq]$ ]] && break'
        )
        
        fpath.write_bytes(raw)
        print(f"Successfully patched {fpath}")
