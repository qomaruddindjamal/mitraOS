# Script Pembuatan & Peluncuran VM Hyper-V mitraOS_V1
$ErrorActionPreference = "Stop"

$vmName = "mitraOS_V1"
$isoPath = "C:\mitraOS\build\mitraOS_V1.iso"
$vhdPath = "C:\mitraOS\build\mitraOS_V1_Disk.vhdx"

Write-Host "1. Memeriksa file ISO..." -ForegroundColor Cyan
if (-not (Test-Path $isoPath)) {
    throw "File ISO tidak ditemukan di: $isoPath"
}
Write-Host "   ISO ditemukan ($([math]::Round((Get-Item $isoPath).Length / 1MB, 1)) MB)" -ForegroundColor Green

Write-Host "2. Memeriksa keberadaan VM lama..." -ForegroundColor Cyan
$existingVM = Get-VM -Name $vmName -ErrorAction SilentlyContinue
if ($existingVM) {
    Write-Host "   Menghentikan dan menghapus VM lama $vmName..." -ForegroundColor Yellow
    if ($existingVM.State -ne 'Off') {
        Stop-VM -Name $vmName -TurnOff -Force
    }
    Remove-VM -Name $vmName -Force
}

Write-Host "3. Menyiapkan Virtual Hard Disk (VHDX)..." -ForegroundColor Cyan
if (Test-Path $vhdPath) {
    Remove-Item -Path $vhdPath -Force
}
New-VHD -Path $vhdPath -SizeBytes 20GB -Dynamic | Out-Null
Write-Host "   VHDX berhasil dibuat: $vhdPath" -ForegroundColor Green

Write-Host "4. Membuat VM Generasi 2 di Hyper-V..." -ForegroundColor Cyan
New-VM -Name $vmName -Generation 2 -MemoryStartupBytes 1024MB -VHDPath $vhdPath -SwitchName "Default Switch" | Out-Null

Write-Host "5. Mengonfigurasi Memori Dinamis..." -ForegroundColor Cyan
Set-VMMemory -VMName $vmName -DynamicMemoryEnabled $true -MinimumBytes 512MB -StartupBytes 1024MB -MaximumBytes 2048MB

Write-Host "6. Memasang DVD Drive dengan file ISO MitraOS..." -ForegroundColor Cyan
$dvd = Add-VMDvdDrive -VMName $vmName -Path $isoPath -Passthru

Write-Host "7. Menonaktifkan Secure Boot & Mengatur Prioritas Boot DVD..." -ForegroundColor Cyan
Set-VMFirmware -VMName $vmName -EnableSecureBoot Off
Set-VMFirmware -VMName $vmName -FirstBootDevice $dvd

Write-Host "8. Menyalakan Virtual Machine $vmName..." -ForegroundColor Green
Start-VM -Name $vmName

Write-Host "9. Memeriksa Status Akhir Virtual Machine:" -ForegroundColor Cyan
Get-VM -Name $vmName | Select-Object Name, State, CPUUsage, MemoryAssigned, Uptime | Format-Table -AutoSize
