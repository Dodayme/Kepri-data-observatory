$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Push-Location (Join-Path $root 'backend')
try {
    & ./.venv/Scripts/python.exe -m ruff check app tests
    if ($LASTEXITCODE -ne 0) { throw 'Pemeriksaan Python gagal.' }
    & ./.venv/Scripts/python.exe -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Pytest gagal.' }
} finally { Pop-Location }
Push-Location (Join-Path $root 'frontend')
try {
    & npm.cmd test
    if ($LASTEXITCODE -ne 0) { throw 'Pengujian frontend gagal.' }
    & npm.cmd run build
    if ($LASTEXITCODE -ne 0) { throw 'Build frontend gagal.' }
} finally { Pop-Location }
