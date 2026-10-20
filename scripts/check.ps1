param([string]$PythonExe = $env:KEPRI_PYTHON)
$ErrorActionPreference = 'Continue'
foreach ($name in @('python','py','node','npm.cmd','git','winget')) {
    Write-Host "`n$name" -ForegroundColor Cyan
    if (Get-Command $name -ErrorAction SilentlyContinue) { & $name --version; if ($LASTEXITCODE -ne 0) { Write-Warning "$name tersedia sebagai perintah tetapi gagal (exit $LASTEXITCODE)." } } else { Write-Warning "$name tidak ditemukan." }
}
$root = Split-Path $PSScriptRoot -Parent
$venv = Join-Path $root 'backend/.venv/Scripts/python.exe'
if (Test-Path $venv) { & $venv -c "import sys; print(sys.executable); import fastapi, sklearn, pandas; print('Dependency backend tersedia')" }
if ($PythonExe) { & $PythonExe --version }
Write-Host 'Python harus 3.11/3.12. Node harus LTS yang kompatibel (disarankan 22 atau 24).'
Write-Host 'check.ps1 hanya membaca environment; tidak menginstal atau mengubah konfigurasi sistem.'
