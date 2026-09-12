$vm = Get-CimInstance -Namespace root\virtualization\v2 -ClassName Msvm_ComputerSystem -Filter "ElementName='mitraOS_V1'"
$vsms = Get-CimInstance -Namespace root\virtualization\v2 -ClassName Msvm_VirtualSystemManagementService
$res = Invoke-CimMethod -InputObject $vsms -MethodName GetVirtualSystemThumbnailImage -Arguments @{
    TargetSystem = $vm
    WidthPixels = [uint16]800
    HeightPixels = [uint16]600
}

if ($res.ImageData) {
    [IO.File]::WriteAllBytes('C:\mitraOS\build\vm_screen.png', $res.ImageData)
    Write-Host "Thumbnail saved successfully ($($res.ImageData.Length) bytes)"
} else {
    Write-Host "No image data returned from Hyper-V"
}
