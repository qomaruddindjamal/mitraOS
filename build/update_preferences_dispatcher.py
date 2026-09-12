from pathlib import Path

repo_root = Path("c:/mitraOS")

dispatcher = """#!/bin/bash
#//////////////////////////////////////////////////////////////////
# MitraOS System Preferences Launcher & Dispatcher
# Dual Mode: GUI Native Control Center & CLI Whiptail Settings
# Founder: Qomaruddin Djamal - Mitra Utama Group
# Location: /usr/bin/mitra-preferences
#//////////////////////////////////////////////////////////////////

CLI_BIN="/usr/bin/mitra-preferences-cli"
[ ! -x "$CLI_BIN" ] && CLI_BIN="/opt/mitraos/bin/mitra-preferences-cli"
[ ! -x "$CLI_BIN" ] && CLI_BIN="$(dirname "$0")/mitra-preferences-cli"

GUI_SCRIPT="/usr/share/mitraos/ui/preferences.tcl"

# 1. Force CLI Mode via flags
if [ "$1" = "--cli" ] || [ "$1" = "-c" ] || [ "$1" = "--tui" ]; then
    shift
    exec "$CLI_BIN" "$@"
fi

# 2. Non-GUI / Non-X11 / Headless / SSH Console
if [ -z "$DISPLAY" ]; then
    exec "$CLI_BIN" "$@"
fi

# 3. Explicit GUI flag
if [ "$1" = "--gui" ] || [ "$1" = "-g" ]; then
    shift
    if [ -x /usr/bin/wish ] && [ -f "$GUI_SCRIPT" ]; then
        exec /usr/bin/wish "$GUI_SCRIPT" "$@"
    fi
fi

# 4. Interactive Terminal Shell (e.g. user typed 'mitra preferences' or 'mitra-preferences' in terminal)
# In terminal, run CLI mode directly so terminal workflow is 100% uninterrupted
if [ -t 0 ]; then
    exec "$CLI_BIN" "$@"
fi

# 5. Desktop Dock / Menu Launcher (invoked without TTY)
# Launch Native Graphical Preferences Window
if [ -x /usr/bin/wish ] && [ -f "$GUI_SCRIPT" ]; then
    exec /usr/bin/wish "$GUI_SCRIPT" "$@"
fi

# 6. Fallback if GUI engine is missing: launch terminal with CLI mode
if [ -x /usr/bin/mitra-terminal ]; then
    exec /usr/bin/mitra-terminal -title "System Preferences" -e "$CLI_BIN" "$@"
elif [ -x /usr/bin/xterm ]; then
    exec /usr/bin/xterm -geometry 94x28+40+35 -bg '#0a0e17' -fg '#e2e8f0' -cr '#00f2fe' -ms '#00f2fe' -bd '#00f2fe' -title "System Preferences" -name "mitra-preferences" -class "MitraPreferences" -e "$CLI_BIN" "$@"
else
    exec "$CLI_BIN" "$@"
fi
""".replace("\r\n", "\n")

target_paths = [
    repo_root / "rootfs" / "usr" / "bin" / "mitra-preferences",
    repo_root / "core" / "bin" / "mitra-preferences",
    repo_root / "rootfs" / "opt" / "mitraos" / "bin" / "mitra-preferences"
]

for p in target_paths:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as f:
        f.write(dispatcher.encode("utf-8"))
    print(f"[+] Updated dispatcher at: {p}")
