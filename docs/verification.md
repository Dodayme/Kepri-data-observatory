# Catatan verifikasi pengerjaan

Tanggal: 20 Oktober 2026. Tidak ada hasil model penelitian yang dibuat tanpa eksekusi model.

| Pemeriksaan | Hasil aktual |
|---|---|
| Node / npm / Git | 24.21.0 / 11.19.0 / 2.54.0 |
| Python perintah global | Alias Microsoft Store, bukan interpreter yang dapat digunakan |
| Python launcher `py` | Tidak ditemukan |
| Python runtime Codex | 3.12.14, dapat dipakai untuk inspeksi read-only |
| winget | Gagal, exit -1978335231 |
| Struktur workbook | Master_Integrasi, 49 baris, 33 kolom, 7 wilayah, 2019–2025 |
| Audit puskesmas aktual | 25 ketidaksesuaian; rincian di reference-inspection.json |
| Aritmetika data asli | Lulus empat rasio dan dua normalisasi contoh Bintan 2019, 49 kunci unik, training/testing 35/14 |
| AST Python | Lulus 13 berkas backend |
| Parser TypeScript/TSX | Lulus 7 berkas; compiler parser dari instalasi Cursor digunakan hanya untuk sintaks |
| Parser PowerShell | Lulus empat skrip |
| Virtual environment | Interpreter dibuat, pip bootstrap gagal PermissionError pada direktori sementara |
| Instalasi backend | Gagal resolusi dependency pada environment dengan koneksi dibatasi |
| Instalasi frontend | Gagal ECONNREFUSED proxy 127.0.0.1:9; cache offline ENOTCACHED |
| npm lockfile | Belum terbentuk; resolusi offline juga dicoba dan gagal |
| Pytest | Tidak dapat mulai: No module named pytest |
| Ruff | Tidak dapat mulai: No module named ruff |
| Build frontend | Tidak dapat mulai: tsc tidak ditemukan |
| Vitest | Tidak dapat mulai: vitest tidak ditemukan |
| API hidup / proxy / browser | Belum terverifikasi karena dependency utama belum tersedia |

Tidak ada perubahan PATH, Execution Policy global, registry, proxy sistem, instalasi sistem, atau berkas sumber. Persetujuan instalasi sistem tidak diperlukan setelah interpreter runtime ditemukan; tidak ada instalasi sistem dijalankan.

Langkah berikutnya: jalankan setup.ps1 dari terminal pengguna dengan akses registry dan izin folder sementara, gunakan interpreter Python 3.11/3.12 eksplisit, kemudian test.ps1 dan start.ps1. Simpan package-lock.json yang dihasilkan npm. Bila tes gagal, tangani kegagalan sebelum menyatakan kriteria selesai terpenuhi.
