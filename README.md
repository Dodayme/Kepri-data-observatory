# Observatorium Pembangunan Kepulauan Riau

Aplikasi lokal React/TypeScript + FastAPI untuk penelitian **Analisis Kesenjangan Pembangunan Antarkabupaten/Kota di Provinsi Kepulauan Riau Berdasarkan Indikator Kependudukan, Kemiskinan, Pendidikan, dan Fasilitas Kesehatan Tahun 2019–2025**.

## Status verifikasi pada environment pengerjaan

**Implementasi tersedia, tetapi setup dan pengujian integrasi belum selesai. Jangan menyatakan aplikasi telah lolos seluruh kriteria selesai.**

- Windows: Node 24.21.0, npm 11.19.0, Git 2.54.0 tersedia. `python` adalah alias Store; `py` tidak tersedia. `winget` gagal dengan exit `-1978335231`.
- Python 3.12.14 ditemukan di runtime Codex. Interpreter ini digunakan untuk inspeksi workbook/PDF dan pemeriksaan sintaks, bukan sebagai dependency global aplikasi.
- Pembuatan `backend/.venv` menghasilkan interpreter, tetapi bootstrap pip gagal dengan `PermissionError` pada direktori sementara. Dependency backend belum terpasang di virtual environment.
- Instalasi npm gagal: environment menerapkan offline cache dan proxy `http://127.0.0.1:9` yang menolak koneksi. Percobaan cache lokal tidak menyediakan seluruh paket yang diperlukan.
- `package-lock.json` belum dapat dihasilkan karena resolusi dependency tidak berhasil. Setelah jaringan tersedia, `setup.ps1` menjalankan `npm.cmd install` untuk membuatnya; simpan lockfile tersebut, lalu setup berikutnya menggunakan `npm.cmd ci`.
- Pemeriksaan AST Python dan parser skrip PowerShell berhasil. Pemeriksaan data asli dengan openpyxl berhasil: 49 kunci unik, 7 wilayah, 2019–2025, 25 ketidaksesuaian puskesmas, empat rasio Bintan 2019, dua normalisasi contoh, dan jumlah training/testing 35/14.
- Pytest, Ruff, build frontend, Vitest, endpoint hidup, dan pengujian browser belum berhasil dijalankan karena dependency belum tersedia. Tidak ada hasil K-Means/regresi penelitian yang diklaim.

Rincian pembacaan aktual ada di `docs/reference-inspection.json`. Dataset dan PDF sumber tidak disunting. `docs/report-extracted.txt` merupakan ekstraksi teks laporan, bukan dataset.

## Persiapan Windows 11 / PowerShell

Gunakan Python **3.11 atau 3.12** dan Node.js LTS **22 atau 24**, beserta npm. Jangan menginstal sistem tanpa persetujuan pemilik komputer. Jika Python belum ada dan winget berfungsi, perintah yang dapat dijalankan pengguna setelah menyetujui instalasi:

```powershell
winget install --id Python.Python.3.12 --exact --scope user
```

Jika winget bermasalah, gunakan installer resmi dari https://www.python.org/downloads/windows/ dengan cakupan pengguna saat ini. Buka ulang terminal setelah instalasi dan periksa ulang versi. Tidak perlu mengubah Execution Policy global, registry, atau PATH secara manual untuk menjalankan proyek; path interpreter dapat diberikan langsung.

```powershell
.\scripts\check.ps1
.\scripts\setup.ps1 -PythonExe 'C:\path\ke\Python312\python.exe'
.\scripts\test.ps1
.\scripts\start.ps1
```

Jika Python yang kompatibel sudah terdeteksi, cukup `.\scripts\setup.ps1`. Alternatif variabel **sesi**: `$env:KEPRI_PYTHON = 'C:\path\python.exe'`.

Jika skrip lokal diblokir Execution Policy, jalankan hanya proses sementara:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -PythonExe 'C:\path\python.exe'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

Skrip tidak mengubah kebijakan sistem dan tidak meminta administrator. `start.ps1` menjalankan dua proses tersembunyi, memeriksa port/dependency, dan menghentikan keduanya saat Ctrl+C. Jika port 8000/5173 digunakan, hentikan aplikasi pemilik port atau lakukan debugging terpisah. Log startup dapat dilihat melalui cara terpisah di bawah.

Jika instalasi gagal dengan `ECONNREFUSED 127.0.0.1:9` atau `ENOTCACHED`, jalankan setup dari terminal pengguna yang memiliki akses registry sesuai kebijakan jaringan. Proyek tidak menghapus proxy/kebijakan jaringan. Jika `venv/ensurepip` gagal dengan `PermissionError`, jalankan kembali setup dari terminal pengguna yang memiliki izin menulis folder proyek dan TEMP; simpan pesan error jika masih gagal. Skrip tidak menghapus data atau venv secara otomatis.

## Menjalankan terpisah untuk debugging

Terminal backend dari root proyek:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal frontend:

```powershell
Set-Location frontend
npm.cmd run dev
```

- Frontend: http://localhost:5173
- Health: http://127.0.0.1:8000/api/health
- OpenAPI interaktif: http://127.0.0.1:8000/docs
- Skema API: http://127.0.0.1:8000/openapi.json

Vite mem-proxy `/api` ke backend lokal. CORS mengizinkan frontend localhost/127.0.0.1:5173. Bila perlu URL API berbeda, salin `.env.example` ke `frontend/.env.local`, ubah `VITE_API_BASE`, dan mulai ulang Vite. Backend selalu hanya bind loopback pada skrip bawaan.

## Penggunaan dan data

1. Buka **Upload Dataset**. Pilih workbook `.xlsx` maksimal 10 MB dengan sheet `Master_Integrasi`, atau gunakan **Baca workbook lokal**.
2. Periksa preview, masalah sel, kunci wilayah–tahun, audit puskesmas dan sinyal anomali IQR. Isu tidak otomatis dikoreksi atau dihapus.
3. Jalankan **Data Preprocessing**, lihat data sumber, enam indikator satuan asli, normalisasi dan statistiknya.
4. Pilih fitur/K di **K-Means Clustering**, lalu jalankan model. K=2,3,4 semuanya dievaluasi; K dengan Silhouette tertinggi adalah bahan pertimbangan, bukan keputusan wajib.
5. Jalankan **Linear Regression** untuk evaluasi temporal 2019–2023 / 2024–2025.
6. Buka **Hasil Analisis** dan unduh tabel CSV/XLSX. Ekspor hanya tersedia setelah analisis sesi tersebut dijalankan.

Workbook aktual ditemukan di root dengan nama `Data_Sains_Kepri_2019_2025 (12).xlsx` dan laporan `Laporan Project 1.pdf`. Nama sedikit berbeda dari contoh prompt, tetapi struktur sheet telah diperiksa. File di `data/input/*.xlsx` juga dikenali. Tombol lokal membaca file pertama menurut urutan path; gunakan upload untuk memilih workbook secara eksplisit.

Kolom wajib:

```text
Kabupaten_Kota, Tahun, Kemiskinan_Maret_Persen,
Kepadatan_Penduduk_Sumber, Jumlah_Penduduk_Ribu,
SD_Sekolah_Total, SMP_Murid_Total, SMP_Guru_Total,
Kes_Puskesmas, Kes_RumahSakitUmum
```

Audit puskesmas membutuhkan `Kes_PuskesmasRawatInap` dan `Kes_PuskesmasNonRawatInap`; bila tidak ada, aplikasi menyatakan audit tidak tersedia, bukan menyatakan tidak ada masalah. Kolom sumber lain tetap dipertahankan. Dataset berbeda dari cakupan penelitian diberi peringatan. K-Means memerlukan minimal 5 observasi dan cukup vektor unik; regresi referensi memerlukan seluruh tahun 2019–2025, training lebih banyak dari jumlah fitur + 1, serta minimal 2 testing.

Dataset dan hasil disimpan dalam memori satu proses backend, maksimal 10 dataset per proses. ID unik memisahkan hasil tiap unggahan. Restart menghapus sesi; unggah ulang. Tidak ada login atau database eksternal. DELETE endpoint dapat membebaskan satu dataset. File mentah tidak ditulis ulang.

## Metodologi

Empat fitur dihitung di backend:

| Fitur | Rumus / satuan |
|---|---|
| `Rasio_SD_10000` | SD_Sekolah_Total / (Jumlah_Penduduk_Ribu × 1000) × 10000 |
| `Rasio_Murid_Guru_SMP` | SMP_Murid_Total / SMP_Guru_Total |
| `Rasio_Puskesmas_10000` | Kes_Puskesmas / (Jumlah_Penduduk_Ribu × 1000) × 10000 |
| `Rasio_RSU_10000` | Kes_RumahSakitUmum / (Jumlah_Penduduk_Ribu × 1000) × 10000 |

Enam indikator: kemiskinan, kepadatan, dan empat rasio. Min-Max `(x-min)/(max-min)` dipasang pada seluruh dataset untuk eksplorasi preprocessing/clustering; fitur konstan bernilai 0. Missing dan simbol tidak diubah menjadi 0. Pembagi nol/nonpositif menghasilkan rasio tidak valid dan memblokir model jika fitur tersebut dipakai. Tidak ada imputasi atau penghapusan observasi otomatis. Validasi model berfokus pada input model; isu kolom lain tetap dilaporkan pada audit.

Kolom rasio sumber dengan nama sama disimpan sebagai `Sumber__<nama>` pada salinan kerja; nilai asli tersedia di preview/preprocessing. Perbandingan normalisasi mengenali `<fitur>__norm`, `<fitur>_Normalized`, `<fitur>_Normalisasi` dengan toleransi absolut 0,0001. Nama normalisasi berbeda harus ditinjau manual. Workbook referensi tidak memiliki kolom rasio/normalisasi tersebut.

K-Means default: kemiskinan, kepadatan, murid/guru SMP, RSU/10.000. `random_state=42`, `n_init=20`. PCA dua komponen hanya visualisasi dari fitur yang telah dinormalisasi; proporsi variasi ditampilkan. Ringkasan wilayah adalah distribusi label, termasuk seluruh modus bila seri, bukan melatih ulang model pada rerata wilayah. Profil rendah/menengah/tinggi menggunakan posisi rerata pada rentang Min-Max (≤1/3, ≥2/3), sehingga bukan klasifikasi pembangunan resmi. Puskesmas diblokir dari model utama dan hanya tersedia dalam eksperimen sensitivitas yang dinyatakan eksplisit.

Regresi default: kepadatan, murid/guru SMP, RSU/10.000; SD dapat ditambahkan. Target atau turunan target tidak dapat dipilih sebagai X. Data diurutkan tahun/wilayah; training 2019–2023, testing 2024–2025; tahun lain diabaikan dan jumlahnya dikembalikan API. Scaler hanya di-fit pada X training. MAE/RMSE memakai poin persentase, R² negatif dipertahankan; R² untuk target testing konstan ditampilkan tidak tersedia. Baseline = rerata Y training. Koefisien skala Min-Max dan satuan asli, intercept, residual, kesalahan wilayah dan flag di luar rentang training ditampilkan. Tidak ada clipping prediksi dan tidak ada prediksi otomatis 2026.

Keterbatasan: sampel kecil, observasi panel berulang, kemungkinan ketergantungan temporal/spasial, tidak ada kontrol panel/kausal, satu holdout temporal, fasilitas bukan ukuran mutu/kapasitas/akses, serta inkonsistensi kesehatan yang belum diverifikasi. Label `ASLI`/`4/4` bukan bukti validasi sumber resmi. Nomor cluster bukan peringkat kemajuan; koefisien bukan pengaruh kausal.

## API

Semua respons JSON kecuali ekspor. Kesalahan: `{"detail":"pesan bahasa Indonesia"}`; validasi skema Pydantic dapat berupa array detail. Dataset ID tidak boleh dipakai silang. OpenAPI `/docs` memuat skema request/response request secara interaktif; contoh respons berikut menunjukkan struktur, bukan nilai hasil penelitian.

| Metode | Endpoint | Request / respons utama |
|---|---|---|
| GET | `/api/health` | status, storage, max_upload_mb |
| GET | `/api/reference` | daftar nama workbook lokal |
| POST | `/api/datasets/reference` | tanpa body; id, filename, rows, columns |
| POST | `/api/datasets/upload` | multipart `file`; id, filename, rows, columns |
| GET | `/api/datasets/{id}/summary` | identitas, preview, regions, years, features |
| GET | `/api/datasets/{id}/quality` | issues, duplicates, audit puskesmas, cakupan, sinyal IQR |
| POST | `/api/datasets/{id}/preprocess` | `{}`; original, engineered, normalized, statistics, descriptive, source_comparisons |
| POST | `/api/datasets/{id}/kmeans` | features, k, sensitivity; members, centroid, evaluations, PCA, profiles, regional_summary |
| POST | `/api/datasets/{id}/regression` | features; metrics, baseline_metrics, predictions, coefficients, intercept, warnings |
| GET | `/api/datasets/{id}/export/{analysis}?format=csv` | analysis = preprocess/kmeans/regression; format = csv/xlsx |
| DELETE | `/api/datasets/{id}` | menghapus salinan sesi dalam memori |

Contoh request K-Means:

```json
{"features":["Kemiskinan_Maret_Persen","Kepadatan_Penduduk_Sumber","Rasio_Murid_Guru_SMP","Rasio_RSU_10000"],"k":3,"sensitivity":false}
```

Contoh request regresi:

```json
{"features":["Kepadatan_Penduduk_Sumber","Rasio_Murid_Guru_SMP","Rasio_RSU_10000"]}
```

Kode status utama: 404 ID/file tidak ditemukan, 409 analisis belum dijalankan/batas sesi, 413 file terlalu besar, 415 ekstensi salah, 422 workbook/input/model tidak valid. File terkompresi dengan ukuran isi >100 MB ditolak; dataset dibatasi 10.000 baris dan 200 kolom.

## Pengujian

```powershell
.\scripts\test.ps1
```

Backend: pembacaan sheet/kolom, kunci, empat rasio, normalisasi/konstan, missing/pembagi nol, audit puskesmas, K-Means/label/PCA/inertia/Silhouette, determinisme, holdout waktu, batas scaler training untuk mencegah leakage, metrik, valid/invalid API, ekspor dan isolasi sesi. Test data asli dijalankan hanya bila workbook ditemukan. Fixture sintetis bernama `SINTETIS_TEST_*` hanya terdapat di tests, tidak dipakai aplikasi.

Frontend: enam navigasi, empty state, unggahan berhasil/gagal, pemilihan parameter, data tabel API, loading, error, dan peringatan sumber. Pengujian browser end-to-end/responsivitas perlu dilakukan setelah dependency tersedia; jangan menyamakan tes DOM dengan tes browser nyata.

Inspeksi referensi terpisah, menggunakan Python yang memiliki openpyxl/pypdf:

```powershell
python .\scripts\inspect_reference.py
python .\scripts\validate_reference_stdlib.py
```

Skrip kedua memeriksa rumus dengan aritmetika langsung dan openpyxl; **bukan** pengganti tes implementasi scikit-learn/API.

## Struktur proyek

```text
backend/
  app/
    api/routes.py
    schemas/analysis.py
    services/preprocessing.py
    services/clustering.py
    services/regression.py
    main.py
  tests/
  requirements.txt
  pyproject.toml
frontend/
  src/           # React, API client, tipe, styling, tests
  package.json
  vite.config.ts
  tsconfig.json
scripts/
  check.ps1
  setup.ps1
  start.ps1
  test.ps1
  inspect_reference.py
  validate_reference_stdlib.py
data/input/
docs/
.env.example
.gitignore
```

Dependency backend dipin di `requirements.txt`. Dependency frontend dicantumkan di `package.json`; lockfile harus dihasilkan dan disimpan setelah instalasi pertama berhasil. Paket utama: FastAPI/Uvicorn, pandas/NumPy, scikit-learn, OpenPyXL, Pydantic/multipart; React/Vite/TypeScript, Tailwind 4 dengan plugin Vite, Router, Recharts, Lucide; Pytest/httpx/Ruff dan Vitest/Testing Library untuk pemeriksaan.
