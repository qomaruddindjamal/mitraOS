import subprocess
import time
import os
from PIL import Image

VM_NAME = "mitraOS_V1"
ISO_PATH = r"C:\mitraOS\build\mitraOS_V1.iso"
ARTIFACT_DIR = r"C:\Users\Administrator\.gemini\antigravity-ide\brain\1ea60939-1e52-44b3-a21f-039a0151abea"

def run_ps(cmd):
    return subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)

print("1. Stopping VM if running...")
run_ps(f"Stop-VM -Name {VM_NAME} -TurnOff -Force")
time.sleep(1.5)

print("2. Setting ISO and boot order...")
setup_ps = f"""
Set-VMDvdDrive -VMName {VM_NAME} -Path '{ISO_PATH}'
$dvd = Get-VMDvdDrive -VMName {VM_NAME}
Set-VMFirmware -VMName {VM_NAME} -FirstBootDevice $dvd
Set-VMMemory -VMName {VM_NAME} -StartupBytes 1024MB
Start-VM -Name {VM_NAME}
"""
res = run_ps(setup_ps)
print("VM Start result:", res.stdout.strip())
if res.stderr.strip():
    print("Stderr:", res.stderr.strip())

def capture_screen(name, w=800, h=600):
    ps_cap = f"""
$vsms = Get-CimInstance -Namespace root\\virtualization\\v2 -ClassName Msvm_VirtualSystemManagementService
$vm = Get-CimInstance -Namespace root\\virtualization\\v2 -ClassName Msvm_ComputerSystem | Where-Object {{ $_.ElementName -eq '{VM_NAME}' }} | Select-Object -First 1
$res = Invoke-CimMethod -InputObject $vsms -MethodName GetVirtualSystemThumbnailImage -Arguments @{{
    TargetSystem = [Microsoft.Management.Infrastructure.CimInstance]$vm
    WidthPixels = [uint16]{w}
    HeightPixels = [uint16]{h}
}}
if ($res -and $res.ImageData) {{
    [System.IO.File]::WriteAllBytes('C:\\mitraOS\\vm_thumb.bin', $res.ImageData)
    Write-Host "OK"
}}
"""
    run_ps(ps_cap)
    bin_path = r"C:\mitraOS\vm_thumb.bin"
    if os.path.exists(bin_path):
        with open(bin_path, "rb") as f:
            raw = f.read()
        expected = w * h * 2
        if len(raw) >= expected:
            img = Image.frombytes("RGB", (w, h), raw[:expected], "raw", "BGR;16")
            png_path = os.path.join(ARTIFACT_DIR, f"{name}.png")
            img.save(png_path)
            local_png = os.path.join(r"C:\mitraOS", f"{name}.png")
            img.save(local_png)
            print(f"[+] Captured {name} ({w}x{h}) -> {png_path}")
            return png_path
    print(f"[-] Failed to capture {name}")
    return None

print("3. Waiting for boot menu (2.5s)...")
time.sleep(2.5)
capture_screen("mitraos_desktop_boot_menu", 800, 600)

print("4. Waiting for live boot sequence (10s)...")
time.sleep(10)
capture_screen("mitraos_desktop_booting", 800, 600)

print("5. Waiting for desktop to render on screen (8s)...")
time.sleep(8)
capture_screen("mitraos_desktop_live_screen", 800, 600)

print("Done testing boot!")
