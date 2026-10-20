import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler
from app.services.preprocessing import FEATURES, KEYS, RATIOS, model_data, records


def cluster(frame, config):
    features = config.features
    if len(set(features)) != len(features) or any(f not in FEATURES for f in features):
        raise ValueError('Pilih fitur clustering unik dari enam indikator yang tersedia.')
    if RATIOS[2] in features and not config.sensitivity:
        raise ValueError('Rasio puskesmas hanya tersedia dalam eksperimen sensitivitas yang dinyatakan eksplisit.')
    data = model_data(frame, features)
    if len(data) < 5:
        raise ValueError('Evaluasi K=2,3,4 memerlukan minimal 5 observasi.')
    scaler = MinMaxScaler()
    x = scaler.fit_transform(data[features])
    distinct = len(np.unique(x, axis=0))
    evaluations, models = [], {}
    for k in [2, 3, 4]:
        if distinct < k:
            evaluations.append({'k': k, 'inertia': None, 'silhouette': None, 'counts': {}, 'warning': 'Vektor unik lebih sedikit dari K.'})
            continue
        model = KMeans(n_clusters=k, random_state=42, n_init=20).fit(x)
        labels = model.labels_
        counts = {str(i): int((labels == i).sum()) for i in range(k)}
        score = float(silhouette_score(x, labels)) if 1 < len(set(labels)) < len(x) else None
        evaluations.append({'k': k, 'inertia': float(model.inertia_), 'silhouette': score, 'counts': counts, 'warning': 'Ada cluster dengan satu anggota.' if min(counts.values()) == 1 else None})
        models[k] = model
    if config.k not in models:
        raise ValueError('K terpilih melebihi jumlah vektor fitur unik.')
    model = models[config.k]
    data['cluster'] = model.labels_.astype(int)
    pca = PCA(n_components=2)
    coordinates = pca.fit_transform(x)
    profiles = []
    for label, group in data.groupby('cluster'):
        means = group[features].mean()
        relative = scaler.transform(means.to_frame().T)[0]
        descriptions = [f'{feature}: relatif {"tinggi" if v >= .67 else "rendah" if v <= .33 else "menengah"} (rerata {means[feature]:.4f})' for feature, v in zip(features, relative)]
        profiles.append({'cluster': int(label), 'jumlah': len(group), **means.to_dict(), 'interpretasi': '; '.join(descriptions)})
    regional = []
    for name, group in data.groupby('Kabupaten_Kota'):
        counts = group['cluster'].value_counts()
        modes = counts[counts == counts.max()].index.tolist()
        regional.append({'Kabupaten_Kota': name, 'observasi': len(group), 'distribusi': {str(k): int(v) for k, v in counts.items()}, 'cluster_modus': sorted(int(i) for i in modes)})
    scores = [e for e in evaluations if e['silhouette'] is not None]
    best = max(scores, key=lambda e: e['silhouette'])['k'] if scores else None
    return {'features': features, 'k': config.k, 'random_state': 42, 'n_init': 20, 'sensitivity': config.sensitivity, 'evaluations': evaluations, 'suggested_k_by_silhouette': best, 'members': records(data[KEYS + features + ['cluster']]), 'pca': records(data[KEYS + ['cluster']].assign(pc1=coordinates[:, 0], pc2=coordinates[:, 1])), 'pca_explained_variance': [float(v) for v in pca.explained_variance_ratio_], 'centroids_normalized': model.cluster_centers_.tolist(), 'centroids_original': scaler.inverse_transform(model.cluster_centers_).tolist(), 'profiles': profiles, 'regional_summary': regional, 'notes': ['Nomor cluster bukan peringkat pembangunan.', 'PCA hanya visualisasi; K-Means memakai fitur Min-Max.', 'Ringkasan wilayah adalah distribusi label observasi, bukan model baru pada rerata wilayah.'] + (['EKSPERIMEN: rasio puskesmas belum diverifikasi.'] if RATIOS[2] in features else [])}
