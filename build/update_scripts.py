#!/usr/bin/env python3
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
bin_dir = REPO_ROOT / "core" / "bin"

pattern = re.compile(
    r'\tif \[\[ -f "\$_DIR/\.\./lib/mitra-globals" \]\]; then.*?'
    r'echo "Error: mitra-globals not found\.".*?'
    r'exit 1\s*\n\tfi',
    re.DOTALL
)

replacement = '''\t# Load Globals with broad discovery
\tfor _g in \\
\t\t"$_DIR/../lib/mitra-globals" \\
\t\t"$_DIR/mitra-globals" \\
\t\t"$_DIR/func/mitra-globals" \\
\t\t"$_DIR/func/apollo-globals" \\
\t\t"/boot/apollo/func/mitra-globals" \\
\t\t"/boot/apollo/func/apollo-globals" \\
\t\t"/boot/apollo/mitra-globals" \\
\t\t"/boot/mitraos/func/mitra-globals" \\
\t\t"/opt/mitraos/lib/mitra-globals" \\
\t\t"/cdrom/mitraos/lib/mitra-globals" \\
\t\t"/cdrom/apollo/func/apollo-globals" \\
\t\t"/cdrom/apollo/tools/mitra-globals" \\
\t\t"/bin/mitra-globals" \\
\t\t"/usr/bin/mitra-globals"; do
\t\tif [[ -f "$_g" ]]; then
\t\t\t. "$_g" 2>/dev/null || true
\t\t\tbreak
\t\tfi
\tdone

\tif ! declare -F G_CHECK_ROOT_USER >/dev/null 2>&1; then
\t\tG_CHECK_ROOT_USER() { :; }
\tfi
\tif ! declare -F G_WHIP_MSG >/dev/null 2>&1; then
\t\tG_WHIP_MSG() { whiptail --title "$1" --msgbox "$2" "${3:-10}" "${4:-60}" 2>/dev/null || echo -e "\\n[$1] $2\\n"; }
\tfi'''

count = 0
for f in sorted(bin_dir.glob("mitra-*")):
    content = f.read_text(encoding="utf-8", errors="ignore")
    if "Error: mitra-globals not found." in content:
        new_content = pattern.sub(replacement, content)
        if new_content != content:
            f.write_text(new_content, encoding="utf-8")
            print(f"Updated {f.name}")
            count += 1
        else:
            print(f"Pattern did not match {f.name}")

print(f"Total updated: {count}")
