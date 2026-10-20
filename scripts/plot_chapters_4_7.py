from pathlib import Path
import json
import os
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/project2"
D = json.loads((OUT / "analysis_results.json").read_text(encoding="utf-8"))
F = OUT / "figures"
F.mkdir(exist_ok=True)
df = pd.DataFrame(D["data"])
target = "Kemiskinan_Maret_Persen"
short = {"Kota Batam": "Batam", "Kota Tanjung Pinang": "Tanjungpinang",
         "Kepulauan Anambas": "Anambas"}
df["Wilayah"] = df.Kabupaten_Kota.replace(short)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 130})
def save(name):
    plt.tight_layout()
    plt.savefig(F / f"{name}.png", dpi=180, bbox_inches="tight")
    plt.close()

fig, ax = plt.subplots(figsize=(8, 3))
ax.hist(df[target], bins=[3,5,7,9,11,13,15], color="#236a8a", edgecolor="white")
ax.set(xlabel="Kemiskinan (%)", ylabel="Jumlah observasi wilayah-tahun",
       title="Distribusi 49 observasi, 2019-2025")
save("4_1_distribusi")
fig, ax = plt.subplots(figsize=(8, 3.2))
latest = df[df.Tahun == 2025].sort_values(target)
ax.barh(latest.Wilayah, latest[target], color="#236a8a")
for i,v in enumerate(latest[target]): ax.text(v+.08,i,f"{v:.2f}",va="center")
ax.set(xlim=(0,10),xlabel="Kemiskinan (%)", title="Seluruh tujuh wilayah pada 2025")
save("4_2_peringkat")
fig, ax = plt.subplots(figsize=(8, 3.4))
for name,g in df.groupby("Wilayah"):
    ax.plot(g.Tahun,g[target],marker="o",markersize=3,label=name)
ax.set(xlabel="Tahun",ylabel="Kemiskinan (%)")
ax.legend(ncol=4,loc="upper center",bbox_to_anchor=(.5,1.25),fontsize=8,frameon=False)
save("4_3_tren")
fig,ax=plt.subplots(figsize=(8,3.2))
for name,g in df.groupby("Wilayah"):
    ax.scatter(g.Rasio_Murid_Guru_SMP,g[target],label=name,s=25,alpha=.8)
ax.set(xlabel="Murid per guru SMP (orang/orang)",ylabel="Kemiskinan (%)")
ax.legend(ncol=4,loc="upper center",bbox_to_anchor=(.5,1.25),fontsize=8,frameon=False)
save("4_4_scatter")
pivot=df.pivot(index="Wilayah",columns="Tahun",values=target)
fig,ax=plt.subplots(figsize=(8,3.3))
im=ax.imshow(pivot.values,cmap="YlOrRd",aspect="auto",vmin=3,vmax=15)
ax.set_xticks(range(7),pivot.columns)
ax.set_yticks(range(7),pivot.index)
for i in range(7):
    for j in range(7): ax.text(j,i,f"{pivot.iloc[i,j]:.2f}",ha="center",va="center",fontsize=8,
                               color="white" if pivot.iloc[i,j]>10 else "black")
fig.colorbar(im,ax=ax,label="Kemiskinan (%)")
save("4_5_heatmap")
ev=D["clustering"]["evaluations"]
fig,axs=plt.subplots(1,2,figsize=(8,3))
axs[0].plot([e["k"] for e in ev],[e["inertia"] for e in ev],"o-",color="#236a8a")
axs[1].plot([e["k"] for e in ev],[e["silhouette"] for e in ev],"o-",color="#236a8a")
for ax in axs: ax.set_xticks([2,3,4]); ax.set_xlabel("Jumlah cluster (K)")
axs[0].set_ylabel("Inertia / WCSS"); axs[1].set_ylabel("Silhouette Score")
save("6_1_evaluasi_cluster")
pca=pd.DataFrame(D["clustering"]["pca"])
fig,ax=plt.subplots(figsize=(8,3.5))
for label,g in pca.groupby("cluster"):
    ax.scatter(g.pc1,g.pc2,label=f"C{label} (n={len(g)})",s=35)
ax.set(xlabel="PC1 (62,71% variasi)",ylabel="PC2 (17,81% variasi)")
ax.legend(frameon=False,ncol=4)
save("5_1_pca")
pred=pd.DataFrame(D["regression"]["predictions"])
fig,axs=plt.subplots(1,2,figsize=(8,3.1))
axs[0].scatter(pred.aktual,pred.prediksi,c="#236a8a")
axs[0].plot([3,11],[3,11],"--",c="#777777")
axs[0].set(xlabel="Aktual (%)",ylabel="Prediksi (%)",title="Garis putus: prediksi = aktual")
axs[1].scatter(pred.prediksi,pred.residual,c="#236a8a")
axs[1].axhline(0,linestyle="--",c="#777777")
axs[1].set(xlabel="Prediksi (%)",ylabel="Residual (poin persentase)",title="Residual = aktual - prediksi")
save("6_2_regresi")
print("Saved 8 figures:", F)
