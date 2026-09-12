#!/bin/bash
# MitraOS ISO Builder (Linux / Bash Wrapper)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." >/dev/null 2>&1 && pwd)"

OUTPUT="${1:-$REPO_ROOT/build/MitraOS-1.0-x86_64.iso}"

echo -e "\e[1;38;5;45m[*] Menjalankan MitraOS ISO Builder (xorriso / hybrid)...\e[0m"
python3 "$REPO_ROOT/build/build-iso.py" --output "$OUTPUT" "$@"
