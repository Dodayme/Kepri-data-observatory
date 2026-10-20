"""FIXTURE SINTETIS KHUSUS TEST. Bukan dataset penelitian."""
from io import BytesIO
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.routes import DATASETS


@pytest.fixture
def synthetic_frame():
    rng = np.random.default_rng(123)
    rows = []
    for year in range(2019, 2026):
        for region in range(7):
            population = 80 + 17 * region + (year - 2019) * 2
            rows.append({'Kabupaten_Kota': f'SINTETIS_TEST_{region}', 'Tahun': year, 'Kemiskinan_Maret_Persen': 3 + region + rng.uniform(0, 1), 'Kepadatan_Penduduk_Sumber': 20 + region * 100 + (year - 2019) * 5, 'Jumlah_Penduduk_Ribu': population, 'SD_Sekolah_Total': 20 + region * 3, 'SMP_Murid_Total': 900 + region * 110 + rng.uniform(0, 60), 'SMP_Guru_Total': 60 + region * 2, 'Kes_Puskesmas': 5 + region, 'Kes_RumahSakitUmum': 1 + region % 3, 'Kes_PuskesmasRawatInap': 2, 'Kes_PuskesmasNonRawatInap': 3 + region})
    return pd.DataFrame(rows)


def workbook_bytes(frame, sheet='Master_Integrasi'):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        frame.to_excel(writer, sheet_name=sheet, index=False)
    return buffer.getvalue()


@pytest.fixture
def client():
    DATASETS.clear()
    with TestClient(app) as session:
        yield session
    DATASETS.clear()
