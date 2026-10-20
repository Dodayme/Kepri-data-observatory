from pathlib import Path
import numpy as np
import pytest
from app.services.preprocessing import read_workbook, quality, engineer, preprocess, TARGET, DENSITY, RATIOS, model_data
from app.services.clustering import cluster
from app.services.regression import regress, metrics
from app.schemas.analysis import ClusterRequest, RegressionRequest
from conftest import workbook_bytes


def test_workbook_and_required_columns(synthetic_frame):
    assert len(read_workbook(workbook_bytes(synthetic_frame))) == 49
    with pytest.raises(ValueError, match='Master_Integrasi'):
        read_workbook(workbook_bytes(synthetic_frame, sheet='SALAH'))
    with pytest.raises(ValueError, match='Kolom wajib'):
        read_workbook(workbook_bytes(synthetic_frame.drop(columns=[TARGET])))
    with pytest.raises(ValueError):
        read_workbook(b'bukan zip')


def test_keys_and_missing(synthetic_frame):
    frame = synthetic_frame.copy()
    frame.loc[1, ['Kabupaten_Kota','Tahun']] = frame.loc[0, ['Kabupaten_Kota','Tahun']].values
    assert len(quality(frame)['duplicates']) == 2
    with pytest.raises(ValueError, match='Kunci'):
        model_data(frame, [TARGET])
    frame = synthetic_frame.copy()
    frame.loc[0,'Tahun'] = 2020.5
    assert quality(frame)['invalid_keys'] == 1
    frame = synthetic_frame.copy()
    frame.loc[0,'Kabupaten_Kota'] = None
    assert quality(frame)['invalid_keys'] == 1
    frame = synthetic_frame.copy()
    frame.loc[0,'Jumlah_Penduduk_Ribu'] = 0
    frame.loc[1,'SMP_Guru_Total'] = np.nan
    data = engineer(frame)
    assert np.isnan(data.loc[0,RATIOS[0]])
    assert np.isnan(data.loc[1,RATIOS[1]])
    assert {'pembagi_nol','missing'}.issubset({r['jenis'] for r in quality(frame)['issues']})
    with pytest.raises(ValueError, match='imputasi'):
        cluster(frame, ClusterRequest())


def test_four_ratios_and_minmax(synthetic_frame):
    row = engineer(synthetic_frame).iloc[0]
    source = synthetic_frame.iloc[0]
    assert row[RATIOS[0]] == pytest.approx(source.SD_Sekolah_Total/source.Jumlah_Penduduk_Ribu*10)
    assert row[RATIOS[1]] == pytest.approx(source.SMP_Murid_Total/source.SMP_Guru_Total)
    assert row[RATIOS[2]] == pytest.approx(source.Kes_Puskesmas/source.Jumlah_Penduduk_Ribu*10)
    assert row[RATIOS[3]] == pytest.approx(source.Kes_RumahSakitUmum/source.Jumlah_Penduduk_Ribu*10)
    result = preprocess(synthetic_frame)
    values = [r[TARGET+'__norm'] for r in result['normalized']]
    assert min(values) == pytest.approx(0)
    assert max(values) == pytest.approx(1)
    frame = synthetic_frame.copy()
    frame[DENSITY] = 9
    assert all(r[DENSITY+'__norm'] == 0 for r in preprocess(frame)['normalized'])


def test_health_symbols_and_original_unchanged(synthetic_frame):
    frame = synthetic_frame.copy()
    frame.loc[0,'Kes_Puskesmas'] += 3
    q = quality(frame)
    assert q['puskesmas_mismatch_count'] == 1
    assert q['puskesmas_mismatches'][0]['selisih'] == 3
    source = frame.copy(deep=True)
    preprocess(frame)
    assert frame.equals(source)
    frame['Kes_RumahSakitUmum'] = frame['Kes_RumahSakitUmum'].astype(object)
    frame.loc[0,'Kes_RumahSakitUmum'] = '-'
    assert quality(frame)['issues'][0]['jenis'] == 'simbol_atau_non_numerik'


def test_source_normalization_comparison_and_negative_r2(synthetic_frame):
    frame = synthetic_frame.copy()
    frame[TARGET+'__norm'] = 9
    frame[RATIOS[0]] = 99
    result = preprocess(frame)
    normalized = next(r for r in result['source_comparisons'] if r['kolom_sumber']==TARGET+'__norm')
    assert normalized['berbeda'] == 49
    assert frame[RATIOS[0]].eq(99).all()
    assert metrics([1,2,3], [20,20,20])['r2'] < 0


def test_clustering(synthetic_frame):
    result = cluster(synthetic_frame, ClusterRequest())
    assert len(result['members']) == 49
    assert sum(p['jumlah'] for p in result['profiles']) == 49
    assert len(result['centroids_normalized']) == 3
    assert all(e['inertia'] >= 0 and -1 <= e['silhouette'] <= 1 for e in result['evaluations'])
    assert result['evaluations'][0]['inertia'] >= result['evaluations'][-1]['inertia']
    assert len(result['pca']) == 49
    assert cluster(synthetic_frame, ClusterRequest())['members'] == result['members']
    with pytest.raises(ValueError, match='sensitivitas'):
        cluster(synthetic_frame, ClusterRequest(features=[TARGET,RATIOS[2]]))
    with pytest.raises(ValueError):
        cluster(synthetic_frame, ClusterRequest(features=['Tahun',TARGET]))


def test_regression_temporal_no_leakage(synthetic_frame):
    frame = synthetic_frame.copy()
    frame.loc[frame.Tahun>=2024,DENSITY] = 100000
    result = regress(frame, RegressionRequest())
    assert result['train_count'] == 35 and result['test_count'] == 14
    assert {r['Tahun'] for r in result['predictions']} == {2024,2025}
    assert result['scaler_fit_scope'] == 'training_only'
    density_coefficient = next(c for c in result['coefficients'] if c['fitur']==DENSITY)
    assert density_coefficient['maksimum_training'] == frame.loc[frame.Tahun<=2023,DENSITY].max()
    assert density_coefficient['maksimum_training'] < frame[DENSITY].max()
    assert result['metrics']['rmse'] >= result['metrics']['mae'] >= 0
    errors = [r['aktual']-r['prediksi'] for r in result['predictions']]
    assert result['metrics']['mae'] == pytest.approx(np.abs(errors).mean())
    assert result['metrics']['rmse'] == pytest.approx(np.sqrt(np.square(errors).mean()))
    assert all(r['di_luar_rentang_training'] for r in result['predictions'])
    with pytest.raises(ValueError):
        regress(frame, RegressionRequest(features=[TARGET]))
    with pytest.raises(ValueError, match='seluruh tahun'):
        regress(frame[frame.Tahun<2025], RegressionRequest())


def test_reference_when_available():
    paths = list(Path(__file__).resolve().parents[2].glob('Data_Sains*.xlsx'))
    if not paths:
        pytest.skip('Workbook penelitian tidak tersedia; tidak dibuat pengganti.')
    frame = read_workbook(paths[0].read_bytes())
    assert quality(frame)['reference_match']
    assert quality(frame)['puskesmas_mismatch_count'] == 25
    bintan = engineer(frame).query('Kabupaten_Kota == "Bintan" and Tahun == 2019').iloc[0]
    assert bintan[RATIOS[0]] == pytest.approx(5.8344, abs=.0001)
    assert bintan[RATIOS[1]] == pytest.approx(15.6794, abs=.0001)
    assert bintan[RATIOS[2]] == pytest.approx(.9410, abs=.0001)
    assert bintan[RATIOS[3]] == pytest.approx(.0627, abs=.0001)
    transformed = preprocess(frame)
    row = next(r for r in transformed['normalized'] if r['Kabupaten_Kota']=='Bintan' and r['Tahun']==2019)
    assert row[TARGET+'__norm'] == pytest.approx(.25, abs=.0001)
    assert row[DENSITY+'__norm'] == pytest.approx(.0521, abs=.0001)
    assert regress(frame, RegressionRequest())['test_count'] == 14
    assert len(cluster(frame, ClusterRequest())['members']) == 49
