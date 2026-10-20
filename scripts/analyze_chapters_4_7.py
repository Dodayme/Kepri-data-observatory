"""Reproduce report calculations without modifying the source workbook."""
from pathlib import Path
import hashlib
import json
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
import numpy as np
import pandas as pd
import sklearn
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import MinMaxScaler
from app.services.preprocessing import (
    read_workbook, engineer, quality, records, FEATURES, CLUSTER_DEFAULT,
    REGRESSION_DEFAULT, TARGET, KEYS,
)
from app.services.clustering import cluster
from app.services.regression import regress, metrics
from app.schemas.analysis import ClusterRequest, RegressionRequest

out = ROOT / "output" / "project2"
out.mkdir(parents=True, exist_ok=True)
source = ROOT / "Data_Sains_Kepri_2019_2025 (12).xlsx"
content = source.read_bytes()
frame = read_workbook(content)
data = engineer(frame).sort_values(KEYS).reset_index(drop=True)
assert len(data) == 49 and not data.duplicated(KEYS).any()
assert data[FEATURES].notna().all().all()
c0 = cluster(frame, ClusterRequest(k=3))
k = c0["suggested_k_by_silhouette"]
c = cluster(frame, ClusterRequest(k=k))
r = regress(frame, RegressionRequest())
# This baseline uses only the latest training-year value for each region.
latest = data[data.Tahun == 2023].set_index("Kabupaten_Kota")[TARGET]
pred = pd.DataFrame(r["predictions"])
pred["baseline_2023"] = pred.Kabupaten_Kota.map(latest)
r["baseline_2023_metrics"] = metrics(pred.aktual, pred.baseline_2023)
r["predictions"] = records(pred)
# Sensitivity removes the remaining health feature with incomplete provenance.
c_nohealth = cluster(frame, ClusterRequest(
    k=k, features=[f for f in CLUSTER_DEFAULT if f != "Rasio_RSU_10000"]))
r_nohealth = regress(frame, RegressionRequest(
    features=[f for f in REGRESSION_DEFAULT if f != "Rasio_RSU_10000"]))
x = MinMaxScaler().fit_transform(
    data.sort_values(["Tahun", "Kabupaten_Kota"])[CLUSTER_DEFAULT])
labels = [row["cluster"] for row in c["members"]]
stability = [
    {"seed": seed, "ari_vs_seed42": float(adjusted_rand_score(
        labels, KMeans(n_clusters=k, random_state=seed, n_init=20).fit_predict(x)))}
    for seed in [0, 1, 7, 21, 99]
]
cols = FEATURES + ["Garis_Kemiskinan_Maret_Rp", "Jumlah_Penduduk_Ribu"]
corr = data[cols].corr()
wide = data.pivot(index="Kabupaten_Kota", columns="Tahun", values=TARGET)
change = pd.DataFrame({"2019": wide[2019], "2025": wide[2025]})
change["perubahan_pp"] = change["2025"] - change["2019"]
q1, q3 = data[TARGET].quantile([.25, .75])
result = {
    "source": source.name, "sha256": hashlib.sha256(content).hexdigest(),
    "versions": {"python": platform.python_version(), "sklearn": sklearn.__version__,
                 "pandas": pd.__version__, "numpy": np.__version__},
    "quality": quality(frame),
    "data": records(data[KEYS + cols]),
    "descriptive": records(data[FEATURES].describe().T.reset_index(names="fitur")),
    "correlation": records(corr.reset_index(names="fitur")),
    "correlation_target": corr[TARGET].to_dict(),
    "change": records(change.reset_index()),
    "poverty_iqr": {"q1": q1, "q3": q3, "lower": q1 - 1.5*(q3-q1),
                    "upper": q3 + 1.5*(q3-q1)},
    "clustering": c, "regression": r,
    "sensitivity": {"clustering_without_rsu": c_nohealth,
                    "ari_same_k_without_rsu": float(adjusted_rand_score(
                        labels, [row["cluster"] for row in c_nohealth["members"]])),
                    "regression_without_rsu": r_nohealth,
                    "seed_stability": stability},
}
(out / "analysis_results.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
pred.to_csv(out / "prediksi_testing.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(c["members"]).to_csv(out / "anggota_cluster.csv", index=False, encoding="utf-8-sig")
data[KEYS + cols].to_csv(out / "data_analisis.csv", index=False, encoding="utf-8-sig")
assert hashlib.sha256(source.read_bytes()).hexdigest() == result["sha256"]
print(json.dumps({
    "k": k, "evaluations": c["evaluations"], "profiles": c["profiles"],
    "regional": c["regional_summary"], "metrics": r["metrics"],
    "mean_baseline": r["baseline_metrics"], "latest_baseline": r["baseline_2023_metrics"],
    "coef": r["coefficients"], "intercept": r["intercept_original"],
    "corr": result["correlation_target"], "change": result["change"],
    "nohealth_metrics": r_nohealth["metrics"],
    "nohealth_ari": result["sensitivity"]["ari_same_k_without_rsu"],
    "pca": c["pca_explained_variance"], "stability": stability,
    "region_errors": r["region_errors"],
}, ensure_ascii=False, indent=2))
