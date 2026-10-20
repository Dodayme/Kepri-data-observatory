param([string]$PythonExe = $env:KEPRI_PYTHON)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
function CheckExit([string]$message) { if ($LASTEXITCODE -ne 0) { throw "$message (exit $LASTEXITCODE). Periksa pesan error, koneksi registry, dan akses folder." } }
Push-Location $root
try {
    if (-not $PythonExe) {
        foreach ($candidate in @('python','py')) {
            if (Get-Command $candidate -ErrorAction SilentlyContinue) {
                $found = & $candidate -c "import sys; print(sys.executable)" 2>$null
                if ($LASTEXITCODE -eq 0) { $PythonExe = [string]$found; break }
            }
        }
    }
    if (-not $PythonExe) { throw 'Python belum tersedia. Instal Python 3.11/3.12 dengan persetujuan pengguna, lalu jalankan setup.ps1 -PythonExe <path-python.exe>.' }
    & $PythonExe -c "import sys; assert sys.version_info[:2] in [(3,11),(3,12)], 'Python harus 3.11 atau 3.12'; print(sys.version)"
    CheckExit 'Versi Python tidak kompatibel'
    if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw 'npm.cmd belum tersedia. Pasang Node.js LTS dengan persetujuan pengguna.' }
    & node -e "const m=+process.versions.node.split('.')[0]; if(![22,24].includes(m)) process.exit(1)"
    CheckExit 'Gunakan Node.js LTS 22/24'
    & $PythonExe -m venv backend/.venv
    CheckExit 'Pembuatan virtual environment gagal'
    & ./backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
    CheckExit 'Instalasi dependency backend gagal'
    Push-Location frontend
    try {
        if (Test-Path package-lock.json) { & npm.cmd ci } else { & npm.cmd install }
        CheckExit 'Instalasi dependency frontend gagal'
    } finally { Pop-Location }
    Write-Host 'Setup selesai. Jalankan .\scripts\test.ps1, kemudian .\scripts\start.ps1' -ForegroundColor Green
} finally { Pop-Location }
