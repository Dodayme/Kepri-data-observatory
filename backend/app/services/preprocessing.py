"""Transformasi eksplisit pada salinan data. Tidak ada imputasi otomatis."""
import json
from io import BytesIO
from zipfile import BadZipFile, ZipFile

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

KEYS = ['Kabupaten_Kota', 'Tahun']
TARGET = 'Kemiskinan_Maret_Persen'
DENSITY = 'Kepadatan_Penduduk_Sumber'
RATIOS = ['Rasio_SD_10000', 'Rasio_Murid_Guru_SMP', 'Rasio_Puskesmas_10000', 'Rasio_RSU_10000']
FEATURES = [TARGET, DENSITY, *RATIOS]
CLUSTER_DEFAULT = [TARGET, DENSITY, RATIOS[1], RATIOS[3]]
REGRESSION_DEFAULT = [DENSITY, RATIOS[1], RATIOS[3]]
RAW_NUMERIC = [TARGET, DENSITY, 'Jumlah_Penduduk_Ribu', 'SD_Sekolah_Total', 'SMP_Murid_Total', 'SMP_Guru_Total', 'Kes_Puskesmas', 'Kes_RumahSakitUmum']
HEALTH = ['Kes_PuskesmasRawatInap', 'Kes_PuskesmasNonRawatInap']
SOURCE_WARNING = 'ASLI dan 4/4 bukan bukti verifikasi sumber resmi. Nol, kosong, dan simbol sumber diperlakukan berbeda. Angka puskesmas tidak dikoreksi otomatis.'


def records(frame):
    return json.loads(frame.to_json(orient='records', force_ascii=False))


def read_workbook(content: bytes):
    try:
        with ZipFile(BytesIO(content)) as z:
            if sum(e.file_size for e in z.infolist()) > 100 * 1024 * 1024:
                raise ValueError('Isi workbook terkompresi melebihi batas 100 MB.')
        with pd.ExcelFile(BytesIO(content), engine='openpyxl') as workbook:
            if 'Master_Integrasi' not in workbook.sheet_names:
                raise ValueError('Sheet Master_Integrasi tidak ditemukan.')
            frame = pd.read_excel(workbook, sheet_name='Master_Integrasi', keep_default_na=False)
    except ValueError:
        raise
    except (BadZipFile, OSError, KeyError, TypeError) as exc:
        raise ValueError('File bukan workbook XLSX yang dapat dibaca.') from exc
    frame = frame.replace('', np.nan).dropna(how='all').reset_index(drop=True)
    if len(frame) == 0 or len(frame) > 10000 or len(frame.columns) > 200:
        raise ValueError('Dataset harus berisi 1–10.000 baris dan maksimal 200 kolom.')
    missing = sorted(set(KEYS + RAW_NUMERIC) - set(frame.columns))
    if missing:
        raise ValueError('Kolom wajib tidak ditemukan: ' + ', '.join(missing))
    return frame


def numeric(frame):
    data = frame.copy(deep=True)
    for column in set(RAW_NUMERIC + HEALTH + ['Tahun']) & set(data.columns):
        data[column] = pd.to_numeric(data[column], errors='coerce').replace([np.inf, -np.inf], np.nan)
    return data


def quality(frame):
    data = numeric(frame)
    issues = []
    for column in RAW_NUMERIC + ['Tahun'] + [c for c in HEALTH if c in frame]:
        for idx in frame.index:
            source = frame.at[idx, column]
            value = data.at[idx, column]
            kind = None
            if pd.isna(source):
                kind = 'missing'
            elif pd.isna(value):
                kind = 'simbol_atau_non_numerik'
            elif value < 0:
                kind = 'nilai_negatif'
            elif column == TARGET and value > 100:
                kind = 'persentase_di_luar_0_100'
            elif column == 'Tahun' and (value % 1 or value < 1900 or value > 2100):
                kind = 'tahun_tidak_valid'
            elif column in ['Jumlah_Penduduk_Ribu', 'SMP_Guru_Total'] and value == 0:
                kind = 'pembagi_nol'
            if kind:
                issues.append({'baris_excel': int(idx + 2), 'kolom': column, 'jenis': kind, 'nilai_sumber': None if pd.isna(source) else str(source)})
    keys = frame[KEYS].copy()
    keys['Kabupaten_Kota'] = keys['Kabupaten_Kota'].astype('string').str.strip().str.casefold()
    keys['Tahun'] = data['Tahun']
    duplicates = records(frame.loc[keys.duplicated(KEYS, keep=False), KEYS])
    invalid_keys = int((frame['Kabupaten_Kota'].isna() | frame['Kabupaten_Kota'].astype(str).str.strip().eq('') | data['Tahun'].isna() | (data['Tahun'] % 1 != 0) | ~data['Tahun'].between(1900, 2100)).sum())
    mismatches = []
    audit_available = all(c in data for c in HEALTH)
    if audit_available:
        diff = data['Kes_Puskesmas'] - data[HEALTH].sum(axis=1, min_count=2)
        mismatches = records(data.loc[diff.notna() & diff.abs().gt(1e-9), KEYS + ['Kes_Puskesmas'] + HEALTH].assign(selisih=diff))
    # Anomali IQR hanya sinyal untuk pemeriksaan, bukan alasan menghapus data.
    outliers = []
    for column in RAW_NUMERIC:
        q1, q3 = data[column].quantile([.25, .75])
        iqr = q3 - q1
        if iqr > 0:
            outliers.extend(records(data.loc[(data[column] < q1 - 1.5 * iqr) | (data[column] > q3 + 1.5 * iqr), KEYS + [column]].assign(indikator=column)))
    regions = sorted(frame['Kabupaten_Kota'].dropna().astype(str).unique().tolist())
    years = sorted(data['Tahun'].dropna().unique().tolist())
    expected_regions = {'Bintan', 'Karimun', 'Kepulauan Anambas', 'Kota Batam', 'Kota Tanjung Pinang', 'Lingga', 'Natuna'}
    reference_match = len(data) == 49 and set(regions) == expected_regions and years == list(range(2019, 2026)) and not duplicates and not invalid_keys
    return {'issues': issues, 'duplicates': duplicates, 'invalid_keys': invalid_keys, 'puskesmas_audit_available': audit_available, 'puskesmas_mismatches': mismatches, 'puskesmas_mismatch_count': len(mismatches), 'outlier_signals': outliers, 'reference_match': reference_match, 'warning': SOURCE_WARNING, 'coverage_warning': None if reference_match else 'Cakupan berbeda dari 7 wilayah × 2019–2025; hasil tidak identik dengan desain penelitian referensi.', 'zero_counts': {c: int(data[c].eq(0).sum()) for c in RAW_NUMERIC}}


def engineer(frame):
    data = numeric(frame)
    population = data['Jumlah_Penduduk_Ribu'].where(data['Jumlah_Penduduk_Ribu'] > 0) * 1000
    derived = {
        RATIOS[0]: data['SD_Sekolah_Total'] / population * 10000,
        RATIOS[1]: data['SMP_Murid_Total'] / data['SMP_Guru_Total'].where(data['SMP_Guru_Total'] > 0),
        RATIOS[2]: data['Kes_Puskesmas'] / population * 10000,
        RATIOS[3]: data['Kes_RumahSakitUmum'] / population * 10000,
    }
    for name, values in derived.items():
        if name in data:
            data['Sumber__' + name] = data[name]
        data[name] = values.replace([np.inf, -np.inf], np.nan)
    return data


def model_data(frame, features):
    audit = quality(frame)
    if audit['duplicates'] or audit['invalid_keys']:
        raise ValueError('Kunci Kabupaten_Kota–Tahun kosong/tidak valid atau duplikat. Perbaiki sumber sebelum analisis.')
    data = engineer(frame)
    # Validasi hanya input yang benar-benar diperlukan model; isu indikator lain tetap ditampilkan.
    required = set(features)
    if any(f.startswith('Rasio_') for f in features):
        if any(f in features for f in [RATIOS[0], RATIOS[2], RATIOS[3]]):
            required.add('Jumlah_Penduduk_Ribu')
        if RATIOS[1] in features:
            required.add('SMP_Guru_Total')
    bad = data[list(required)].isna().any(axis=1) | data[list(required)].lt(0).any(axis=1)
    if TARGET in features:
        bad |= data[TARGET].gt(100)
    if bad.any():
        raise ValueError(f'{int(bad.sum())} observasi memiliki nilai kosong, non-numerik, pembagi tidak valid, atau nilai di luar domain pada fitur terpilih. Tidak ada imputasi/penghapusan otomatis.')
    return data.sort_values(['Tahun', 'Kabupaten_Kota']).reset_index(drop=True)


def preprocess(frame):
    data = engineer(frame)
    normalized = data[KEYS].copy()
    stats = []
    comparisons = []
    for feature in FEATURES:
        series = data[feature]
        valid = series.notna() & np.isfinite(series)
        normalized[feature + '__norm'] = np.nan
        low, high = series.min(), series.max()
        if valid.any():
            normalized.loc[valid, feature + '__norm'] = MinMaxScaler().fit_transform(data.loc[valid, [feature]]).ravel()
        stats.append({'fitur': feature, 'minimum': None if pd.isna(low) else float(low), 'maksimum': None if pd.isna(high) else float(high), 'konstan': bool(low == high), 'valid': int(valid.sum())})
        for candidate in [feature + '__norm', feature + '_Normalized', feature + '_Normalisasi']:
            if candidate in frame:
                original = pd.to_numeric(frame[candidate], errors='coerce')
                computed = normalized[feature + '__norm']
                comparable = original.notna() & computed.notna()
                comparisons.append({'kolom_sumber': candidate, 'dibandingkan': int(comparable.sum()), 'berbeda': int((~np.isclose(original[comparable], computed[comparable], atol=0.0001, rtol=0)).sum()), 'toleransi': 0.0001})
        if feature in frame and feature in RATIOS:
            original = pd.to_numeric(frame[feature], errors='coerce')
            valid_pair = original.notna() & data[feature].notna()
            comparisons.append({'kolom_sumber': feature, 'dibandingkan': int(valid_pair.sum()), 'berbeda': int((~np.isclose(original[valid_pair], data.loc[valid_pair, feature], atol=.0001)).sum()), 'toleransi': .0001})
    return {'original': records(frame), 'engineered': records(data[KEYS + FEATURES]), 'normalized': records(normalized), 'statistics': stats, 'descriptive': records(data[FEATURES].describe().rename_axis('statistik').reset_index()), 'source_comparisons': comparisons, 'quality': quality(frame), 'scaler_scope': 'Seluruh dataset untuk eksplorasi. Regresi memasang scaler terpisah hanya pada training.'}
