$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$python = Join-Path $root 'backend/.venv/Scripts/python.exe'
$vite = Join-Path $root 'frontend/node_modules/vite/bin/vite.js'
if (-not (Test-Path $python) -or -not (Test-Path $vite)) { throw 'Dependency belum lengkap. Jalankan .\scripts\setup.ps1 dahulu.' }
& $python -c 'import fastapi, uvicorn, pandas, sklearn, openpyxl, multipart'
if ($LASTEXITCODE -ne 0) { throw 'Dependency backend belum lengkap. Jalankan setup.ps1.' }
foreach ($port in @(8000,5173)) {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback,$port)
    try { $listener.Start() } catch { throw "Port $port sudah digunakan/tidak dapat dibuka. Hentikan aplikasi pemakai port sebelum mencoba lagi." } finally { $listener.Stop() }
}
$backend = $null
$frontend = $null
try {
    $backend = Start-Process -FilePath $python -ArgumentList @('-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000') -WorkingDirectory (Join-Path $root 'backend') -WindowStyle Hidden -PassThru
    $node = (Get-Command node -ErrorAction Stop).Source
    $frontend = Start-Process -FilePath $node -ArgumentList @(('"' + $vite + '"'),'--host','127.0.0.1','--port','5173','--strictPort') -WorkingDirectory (Join-Path $root 'frontend') -WindowStyle Hidden -PassThru
    Write-Host 'Frontend: http://localhost:5173 | API: http://127.0.0.1:8000 | Dokumentasi: http://127.0.0.1:8000/docs'
    Write-Host 'Tekan Ctrl+C untuk menghentikan kedua proses. Biarkan terminal ini terbuka.'
    while (-not $backend.HasExited -and -not $frontend.HasExited) { Start-Sleep -Milliseconds 700; $backend.Refresh(); $frontend.Refresh() }
    throw 'Salah satu proses berhenti. Jalankan server terpisah sesuai README untuk melihat pesan error.'
} finally {
    foreach ($process in @($backend,$frontend)) { if ($null -ne $process -and -not $process.HasExited) { Stop-Process -Id $process.Id -ErrorAction SilentlyContinue } }
}
