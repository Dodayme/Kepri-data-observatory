"""Pemeriksaan data asli tanpa dependency ML: openpyxl + rumus aritmetika.

Ini bukan pengujian integrasi scikit-learn atau pengganti Pytest.
"""
from pathlib import Path
from openpyxl import load_workbook

root = Path(__file__).resolve().parents[1]
book = next(root.glob('Data_Sains*.xlsx'))
wb = load_workbook(book, read_only=True, data_only=True)
values = list(wb['Master_Integrasi'].values)
rows = [dict(zip(values[0], row)) for row in values[1:]]
assert len(rows) == 49
assert len({(r['Kabupaten_Kota'], r['Tahun']) for r in rows}) == 49
assert len({r['Kabupaten_Kota'] for r in rows}) == 7
assert {r['Tahun'] for r in rows} == set(range(2019, 2026))
assert sum(r['Kes_Puskesmas'] != r['Kes_PuskesmasRawatInap'] + r['Kes_PuskesmasNonRawatInap'] for r in rows) == 25
b = next(r for r in rows if r['Kabupaten_Kota'] == 'Bintan' and r['Tahun'] == 2019)
ratios = [b['SD_Sekolah_Total']/b['Jumlah_Penduduk_Ribu']*10, b['SMP_Murid_Total']/b['SMP_Guru_Total'], b['Kes_Puskesmas']/b['Jumlah_Penduduk_Ribu']*10, b['Kes_RumahSakitUmum']/b['Jumlah_Penduduk_Ribu']*10]
for actual, expected in zip(ratios, [5.8344, 15.6794, .9410, .0627]):
    assert abs(actual-expected)<.0001, (actual, expected)
for column, expected in [('Kemiskinan_Maret_Persen', .25), ('Kepadatan_Penduduk_Sumber', .0521)]:
    low = min(r[column] for r in rows)
    high = max(r[column] for r in rows)
    actual = (b[column]-low)/(high-low)
    assert abs(actual-expected)<.0001, (actual, expected)
assert sum(2019 <= r['Tahun'] <= 2023 for r in rows) == 35
assert sum(2024 <= r['Tahun'] <= 2025 for r in rows) == 14
print('PASS: 49 kunci unik, 7 wilayah, 7 tahun, 25 ketidaksesuaian puskesmas, empat rasio Bintan, dua normalisasi, pembagian 35/14.')
print('Belum memverifikasi implementasi scikit-learn, FastAPI, atau frontend.')
