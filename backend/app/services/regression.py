import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
from app.services.preprocessing import TARGET, DENSITY, RATIOS, KEYS, model_data, records


def metrics(actual, predicted):
    return {'mae': float(mean_absolute_error(actual, predicted)), 'rmse': float(np.sqrt(mean_squared_error(actual, predicted))), 'r2': float(r2_score(actual, predicted)) if np.var(actual) > 0 else None}


def regress(frame, config):
    features = config.features
    allowed = [DENSITY, RATIOS[0], RATIOS[1], RATIOS[3]]
    if len(set(features)) != len(features) or any(f not in allowed for f in features):
        raise ValueError('Fitur X tidak valid. Target, turunan target, identitas, dan puskesmas dilarang.')
    data = model_data(frame, features + [TARGET])
    years = set(data['Tahun'].astype(int))
    if not set(range(2019, 2026)).issubset(years):
        raise ValueError('Evaluasi referensi memerlukan seluruh tahun 2019–2025; tidak dilakukan random split pengganti.')
    train = data[data['Tahun'].between(2019, 2023)]
    test = data[data['Tahun'].between(2024, 2025)]
    if len(train) <= len(features) + 1 or len(test) < 2:
        raise ValueError('Observasi training/testing tidak mencukupi untuk fitur terpilih.')
    scaler = MinMaxScaler().fit(train[features])
    x_train = scaler.transform(train[features])
    x_test = scaler.transform(test[features])
    model = LinearRegression().fit(x_train, train[TARGET])
    predicted = model.predict(x_test)
    baseline_value = float(train[TARGET].mean())
    baseline = np.full(len(test), baseline_value)
    result = test[KEYS + [TARGET]].rename(columns={TARGET: 'aktual'}).copy()
    result['prediksi'] = predicted
    result['baseline'] = baseline
    result['residual'] = result['aktual'] - predicted
    result['absolute_error'] = result['residual'].abs()
    result['di_luar_rentang_training'] = ((x_test < 0) | (x_test > 1)).any(axis=1)
    coefficients = [{'fitur': f, 'koefisien_skala_0_1': float(c), 'koefisien_satuan_asli': float(c * scale), 'minimum_training': float(lo), 'maksimum_training': float(hi)} for f, c, scale, lo, hi in zip(features, model.coef_, scaler.scale_, scaler.data_min_, scaler.data_max_)]
    warnings = ['Asosiasi statistik bukan bukti sebab-akibat.', 'Observasi wilayah berulang tidak independen; model ini belum mengendalikan efek panel atau spasial.', 'Sampel kecil dan hanya satu pemisahan waktu membatasi generalisasi.', 'MAE/RMSE dalam poin persentase; R² negatif tetap ditampilkan.']
    if np.linalg.matrix_rank(x_train) < len(features):
        warnings.append('Matriks fitur tidak berpangkat penuh; koefisien dapat tidak stabil.')
    if result['di_luar_rentang_training'].any():
        warnings.append('Ada observasi testing di luar rentang fitur training; prediksi melibatkan ekstrapolasi.')
    return {'features': features, 'target': TARGET, 'train_years': list(range(2019, 2024)), 'test_years': [2024, 2025], 'train_count': len(train), 'test_count': len(test), 'ignored_year_count': len(data) - len(train) - len(test), 'metrics': metrics(test[TARGET], predicted), 'baseline_metrics': metrics(test[TARGET], baseline), 'baseline_training_mean': baseline_value, 'predictions': records(result), 'coefficients': coefficients, 'intercept_scaled': float(model.intercept_), 'intercept_original': float(model.intercept_ + model.coef_ @ scaler.min_), 'scaler_fit_scope': 'training_only', 'region_errors': records(result.groupby('Kabupaten_Kota', as_index=False)['absolute_error'].mean()), 'warnings': warnings}
