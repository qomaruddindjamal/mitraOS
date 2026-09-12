$vm = Get-CimInstance -Namespace root\virtualization\v2 -ClassName Msvm_ComputerSystem -Filter "ElementName='mitraOS_V1'"
$kbd = Get-CimAssociatedInstance -InputObject $vm -ResultClassName Msvm_Keyboard

# Send newline
Invoke-CimMethod -InputObject $kbd -MethodName TypeText -Arguments @{ asciiText = "`n" } | Out-Null
Start-Sleep -Milliseconds 300
Invoke-CimMethod -InputObject $kbd -MethodName TypeText -Arguments @{ asciiText = "mitra banner`n" } | Out-Null
Start-Sleep -Seconds 2

& 'C:\mitraOS\build\get_screen.ps1'
& python C:\mitraOS\build\decode_screen.py
