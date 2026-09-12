import subprocess
import time
import sys

SCANCODES = {
    '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06,
    '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A, '0': 0x0B,
    '-': 0x0C, '=': 0x0D, ' ': 0x39, '/': 0x35, '.': 0x34, ',': 0x33, ';': 0x27, '\'': 0x28,
    '[': 0x1A, ']': 0x1B, '\\': 0x2B, '`': 0x29,
    'q': 0x10, 'w': 0x11, 'e': 0x12, 'r': 0x13, 't': 0x14,
    'y': 0x15, 'u': 0x16, 'i': 0x17, 'o': 0x18, 'p': 0x19,
    'a': 0x1E, 's': 0x1F, 'd': 0x20, 'f': 0x21, 'g': 0x22,
    'h': 0x23, 'j': 0x24, 'k': 0x25, 'l': 0x26,
    'z': 0x2C, 'x': 0x2D, 'c': 0x2E, 'v': 0x2F, 'b': 0x30,
    'n': 0x31, 'm': 0x32, '\n': 0x1C
}

SHIFT_SCANCODES = {
    '!': 0x02, '@': 0x03, '#': 0x04, '$': 0x05, '%': 0x06, '^': 0x07, '&': 0x08, '*': 0x09,
    '(': 0x0A, ')': 0x0B, '_': 0x0C, '+': 0x0D, '{': 0x1A, '}': 0x1B, '|': 0x2B,
    ':': 0x27, '"': 0x28, '<': 0x33, '>': 0x34, '?': 0x35, '~': 0x29
}

SPECIAL_COMBOS = {
    'ctrl+alt+t': [0x1D, 0x38, 0x14, 0x94, 0xB8, 0x9D],
    'ctrl+space': [0x1D, 0x39, 0xB9, 0x9D],
    'alt+tab': [0x38, 0x0F, 0x8F, 0xB8],
    'enter': [0x1C, 0x9C],
    'esc': [0x01, 0x81],
    'tab': [0x0F, 0x8F],
}

def type_cmd(cmd_string, wait_sec=2.0, vm_target=None):
    clean = cmd_string.strip().lower()
    if clean in SPECIAL_COMBOS:
        bytes_list = SPECIAL_COMBOS[clean]
    else:
        bytes_list = []
        for ch in cmd_string:
            if ch.isupper() and ch.lower() in SCANCODES:
                make = SCANCODES[ch.lower()]
                bytes_list.extend([0x2A, make, make | 0x80, 0xAA])
            elif ch in SHIFT_SCANCODES:
                make = SHIFT_SCANCODES[ch]
                bytes_list.extend([0x2A, make, make | 0x80, 0xAA])
            elif ch.lower() in SCANCODES:
                make = SCANCODES[ch.lower()]
                brk = make | 0x80
                bytes_list.extend([make, brk])
        # Append Enter
        bytes_list.extend([0x1C, 0x9C])
    
    bytes_str = ", ".join(f"0x{b:02X}" for b in bytes_list)
    
    ps_code = f"""
$targetName = '{vm_target if vm_target else ""}'
if ($targetName) {{
    $vm = Get-CimInstance -Namespace root\\virtualization\\v2 -ClassName Msvm_ComputerSystem | Where-Object {{ $_.ElementName -eq $targetName -and $_.EnabledState -eq 2 }} | Select-Object -First 1
}} else {{
    $vm = Get-CimInstance -Namespace root\\virtualization\\v2 -ClassName Msvm_ComputerSystem | Where-Object {{ $_.EnabledState -eq 2 -and ($_.ElementName -match 'mitraOS|MitraOS|ApolloOS') }} | Select-Object -First 1
}}

if (-not $vm) {{
    Write-Host "[-] No running VM found matching criteria"
    exit 1
}}

$kb = Get-CimInstance -Namespace root\\virtualization\\v2 -ClassName Msvm_Keyboard | Where-Object {{ $_.SystemName -eq $vm.Name }} | Select-Object -First 1
if (-not $kb) {{
    Write-Host "[-] Keyboard not found for VM $($vm.ElementName)"
    exit 1
}}

$bytes = [byte[]]@({bytes_str})
foreach ($b in $bytes) {{
    Invoke-CimMethod -InputObject $kb -MethodName TypeScancodes -Arguments @{{ scanCodes = [byte[]]@($b) }} | Out-Null
    Start-Sleep -Milliseconds 20
}}
"""
    ps_path = r"C:\mitraOS\build\_run_cmd.ps1"
    with open(ps_path, "w", encoding="utf-8") as f:
        f.write(ps_code)
        
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_path], check=True)
    time.sleep(wait_sec)
    
    # Capture screen
    cap_vm = "mitraOS"
    if vm_target:
        cap_vm = vm_target
    subprocess.run(["python", r"C:\mitraOS\build\capture_vm_screen.py", cap_vm], check=True)

if __name__ == "__main__":
    target = None
    args = sys.argv[1:]
    if args and args[0].startswith("--vm="):
        target = args[0].split("=")[1]
        args = args[1:]
        
    cmd = " ".join(args)
    if not cmd:
        cmd = "enter"
    type_cmd(cmd, vm_target=target)
