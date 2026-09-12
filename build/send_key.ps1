param(
    [string]$Text = "clear"
)

$vm = Get-CimInstance -Namespace root\virtualization\v2 -ClassName Msvm_ComputerSystem -Filter "ElementName='mitraOS_V1'"
$kbd = Get-CimAssociatedInstance -InputObject $vm -ResultClassName Msvm_Keyboard

if ($kbd) {
    Invoke-CimMethod -InputObject $kbd -MethodName TypeText -Arguments @{ asciiText = "$Text`n" } | Out-Null
    Write-Host "Typed '$Text' into VM successfully!"
} else {
    Write-Host "Keyboard controller not found for VM"
}
