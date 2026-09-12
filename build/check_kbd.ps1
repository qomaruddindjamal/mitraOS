$vm = Get-CimInstance -Namespace root\virtualization\v2 -ClassName Msvm_ComputerSystem -Filter "ElementName='mitraOS_V1'"
$kbd = Get-CimAssociatedInstance -InputObject $vm -ResultClassName Msvm_Keyboard
$kbd.CimClass.CimClassMethods | Select-Object Name
