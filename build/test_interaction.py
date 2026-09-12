import subprocess
import time
from test_boot_desktop import capture_screen, run_ps

ps_key1 = """
$vm = Get-CimInstance -Namespace root\\virtualization\\v2 -ClassName Msvm_ComputerSystem | Where-Object { $_.ElementName -eq 'mitraOS_V1' } | Select-Object -First 1
$kb = Get-CimAssociatedInstance -InputObject $vm -ResultClassName Msvm_Keyboard
Invoke-CimMethod -InputObject $kb -MethodName TypeScancodes -Arguments @{ scanCodes = [byte[]]@(0x02, 0x82) } | Out-Null
"""

print("Pressing key 1 (Mitra Control Center)...")
run_ps(ps_key1)
time.sleep(2.0)
capture_screen("mitraos_desktop_opened_control_center", 800, 600)
print("Captured!")
