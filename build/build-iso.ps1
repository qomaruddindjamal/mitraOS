# MitraOS ISO Builder (PowerShell Native Wrapper)
param (
    [string]$Output = "build/MitraOS-1.0-x86_64.iso",
    [switch]$DryRun,
    [switch]$Clean
)

$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Split-Path -Parent $PSScriptRoot

$cmd = "python `"$RepoRoot\build\build-iso.py`" --output `"$Output`""
if ($DryRun) { $cmd += " --dry-run" }
if ($Clean) { $cmd += " --clean" }

Write-Host "Menjalankan MitraOS ISO Builder..." -ForegroundColor Cyan
Invoke-Expression $cmd
