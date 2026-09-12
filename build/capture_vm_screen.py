import sys
import subprocess
from PIL import Image

vm_name = sys.argv[1] if len(sys.argv) > 1 else 'mitraOS_V1'
out_png = sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\Administrator\.gemini\antigravity-ide\brain\1ea60939-1e52-44b3-a21f-039a0151abea\mitraos_v1_live_screen.png"

ps_cap = f"""
$vsms = Get-CimInstance -Namespace root\\virtualization\\v2 -ClassName Msvm_VirtualSystemManagementService
$vm = Get-CimInstance -Namespace root\\virtualization\\v2 -ClassName Msvm_ComputerSystem | Where-Object {{ $_.ElementName -eq '{vm_name}' }} | Select-Object -First 1
$res = Invoke-CimMethod -InputObject $vsms -MethodName GetVirtualSystemThumbnailImage -Arguments @{{
    TargetSystem = [Microsoft.Management.Infrastructure.CimInstance]$vm
    WidthPixels = [uint16]800
    HeightPixels = [uint16]600
}}
if ($res -and $res.ImageData) {{
    [System.IO.File]::WriteAllBytes('C:\\mitraOS\\vm_mitraos_thumb.bin', $res.ImageData)
    Write-Host "OK"
}} else {{
    Write-Host "NO_IMAGE"
}}
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cap], capture_output=True, text=True)
print("Output:", res.stdout.strip())
if res.stderr.strip():
    print("Error:", res.stderr.strip())

with open(r"C:\mitraOS\vm_mitraos_thumb.bin", "rb") as f:
    raw = f.read()

if len(raw) >= 800 * 600 * 2:
    img = Image.frombytes("RGB", (800, 600), raw[:800 * 600 * 2], "raw", "BGR;16")
    img.save(out_png)
    print(f"[+] Saved {out_png} successfully!")
