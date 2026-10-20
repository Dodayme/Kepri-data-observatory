"""Build the PDF and editable Markdown from verified analysis output."""
from pathlib import Path
import json
from html import escape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/project2"
D = json.loads((OUT / "analysis_results.json").read_text(encoding="utf-8"))
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="BodyReport",fontName="Times-Roman",fontSize=11,
                         leading=15,spaceAfter=8,alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name="SmallReport",fontName="Helvetica",fontSize=8,
                         leading=11,spaceAfter=6))
for name in ["Title","Heading1","Heading2","Heading3"]:
    styles[name].textColor=colors.black
styles["Heading1"].fontSize=17
styles["Heading1"].leading=21
styles["Heading2"].fontSize=12
styles["Heading2"].leading=16
story=[]; md=[]
def h(text,level=2):
    story.append(Paragraph(escape(text),styles["Heading1" if level==1 else "Heading2"]))
    md.extend(["#"*level+" "+text,""])
def p(text):
    story.append(Paragraph(escape(text),styles["BodyReport"]))
    md.extend([text,""])
def small(text):
    story.append(Paragraph(escape(text),styles["SmallReport"]))
    md.extend([text,""])
def page():
    story.append(PageBreak()); md.extend(["---",""])
def table(headers,rows,widths=None):
    cells=[[Paragraph(escape(str(x)),styles["SmallReport"]) for x in row]
           for row in [headers]+rows]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e4edf1")),
        ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#c7cdd0")),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    story.extend([t,Spacer(1,9)])
    md.append("| "+" | ".join(map(str,headers))+" |")
    md.append("| "+" | ".join(["---"]*len(headers))+" |")
    md.extend("| "+" | ".join(map(str,row))+" |" for row in rows);md.append("")
def fig(name,caption,width=460):
    path=OUT/"figures"/f"{name}.png"
    iw,ih=ImageReader(str(path)).getSize()
    story.append(Image(str(path),width=width,height=width*ih/iw))
    small(caption+" Sumber: perhitungan atas Master_Integrasi [1].")
    md.extend([f"![{caption}](figures/{name}.png)",""])
def n(v,d=3): return f"{v:.{d}f}".replace(".",",")
short={"Kota Batam":"Batam","Kota Tanjung Pinang":"Tanjungpinang","Kepulauan Anambas":"Anambas"}

h("LANJUTAN LAPORAN DATA SAINS",1)
h("BAB 4–7 | Kelompok 7",2)
p("Analisis Kesenjangan Pembangunan Antarkabupaten/Kota di Provinsi Kepulauan Riau Berdasarkan Indikator Kependudukan, Kemiskinan, Pendidikan, dan Fasilitas Kesehatan Tahun 2019–2025")
p("Dokumen ini melanjutkan BAB 1–3 pada Laporan Project 1. BAB 4 melengkapi eksplorasi data; BAB 5–7 menyajikan pemodelan, evaluasi, interpretasi, dan rekomendasi untuk Project 2. Susunan mengikuti ketentuan tugas dan rubrik yang diberikan [2,3].")
p("Disusun untuk Kelompok 7: Balqis Manisa, Nabil, Annisa Darmawan, M. Dodi Bastian, Mikael Rejeki Situmorang, dan Yehezkiel Alman Siambaton. Program Studi Teknik Informatika, Universitas Maritim Raja Ali Haji, 2026.")
h("Status dan cakupan")
p("Seluruh angka model dan grafik dalam dokumen ini dihitung dari workbook yang tersedia. Dua algoritma yang dijalankan adalah K-Means dan regresi linear berganda. PCA digunakan sebagai proyeksi visual hasil clustering. Penelitian bersifat eksploratif pada data sekunder, dengan evaluasi regresi menggunakan pemisahan waktu.")
p("Cakupan terdiri atas 49 observasi wilayah-tahun: tujuh kabupaten/kota selama 2019–2025. Hasil menggambarkan indikator terpilih dan tidak menghasilkan indeks pembangunan resmi. Satuan persentase kemiskinan dibedakan dari perubahan atau galat dalam poin persentase.")
h("Catatan sebelum pengumpulan")
p("Ketentuan tugas menyebut sumber Satu Data/data.go.id. Laporan Project 1 menyebut BPS, tetapi URL dataset spesifik dan keterlacakan beberapa nilai kesehatan belum lengkap. Kelompok perlu melengkapi bukti sumber atau mengklarifikasi kesesuaian sumber kepada dosen. Menjalankan model tidak menyelesaikan masalah asal data tersebut.")
table(["Bagian","Isi"],[
    ["BAB 4","Distribusi; lima visualisasi EDA; korelasi; insight awal"],
    ["BAB 5","Pemilihan algoritma; training; testing; parameter; hasil model"],
    ["BAB 6","Silhouette dan Elbow; MAE, RMSE, R²; baseline dan sensitivitas"],
    ["BAB 7","Insight, implikasi, rekomendasi, keterbatasan, dan kesimpulan"],
    ["Lampiran","Prediksi lengkap, bukti implementasi, rubrik, dan alur presentasi"],
],[85,375])
small("Tanggal analisis: 20 Oktober 2026. Dokumen lanjutan; penomoran halaman dimulai kembali.")
page()

h("BAB 4 – Exploratory Data Analysis",1)
h("4.1 Distribusi data")
p("Eksplorasi dilakukan untuk memahami variasi tingkat kemiskinan dan karakteristik layanan sebelum menginterpretasikan model. Unit observasi adalah satu wilayah pada satu tahun; tujuh tahun dari wilayah yang sama bukan tujuh wilayah independen. Statistik gabungan memberi bobot yang sama pada setiap baris, sehingga rerata di bawah bukan persentase kemiskinan provinsi berbobot penduduk.")
labels=["Kemiskinan (%)","Kepadatan (jiwa/km²)","SD/10.000 penduduk","Murid/guru SMP","Puskesmas/10.000","RSU/10.000"]
table(["Indikator","Rerata","Median","Min.","Maks."],[
    [label,n(row["mean"],2),n(row["50%"],2),n(row["min"],2),n(row["max"],2)]
    for label,row in zip(labels,D["descriptive"])
],[160,75,75,75,75])
small("Tabel 4.1. Statistik 49 observasi. Statistik puskesmas ditampilkan untuk audit deskriptif; fitur tersebut dikeluarkan dari model utama.")
fig("4_1_distribusi","Gambar 4.1. Histogram tingkat kemiskinan.")
p("Rerata kemiskinan 7,04% lebih tinggi daripada median 6,42%, sejalan dengan adanya ekor distribusi ke nilai tinggi. Rentangnya 3,81%–14,05%. Kuartil pertama 5,16% dan kuartil ketiga 7,51% menghasilkan batas atas IQR 11,035%. Nilai di atas batas tersebut merupakan sinyal pemeriksaan, bukan alasan otomatis menghapus observasi.")
p("Rentang kepadatan 39–1.614 jiwa/km² menunjukkan perbedaan skala antarwilayah. Normalisasi diperlukan untuk K-Means agar jarak tidak didominasi indikator bersatuan besar. Normalisasi tidak menghilangkan pencilan atau memvalidasi sumber.")
page()

h("4.2 Visualisasi data",1)
fig("4_2_peringkat","Gambar 4.2. Peringkat kemiskinan tahun 2025.")
p("Lingga memiliki tingkat kemiskinan tertinggi pada 2025, sebesar 9,12%, sedangkan Batam terendah, 3,81%; selisihnya 5,31 poin persentase. Karena hanya ada tujuh wilayah, grafik menampilkan seluruh wilayah, bukan memaksakan contoh top 10 pada pedoman.")
fig("4_3_tren","Gambar 4.3. Perubahan kemiskinan menurut wilayah.")
p("Perubahan 2019–2025 berbeda antarwilayah. Lingga turun 3,76 poin persentase dan Tanjungpinang turun 3,07 poin; Anambas turun 0,09 poin, sedangkan Natuna naik 0,39 poin. Penurunan antara dua titik waktu tidak berarti setiap tahun selalu menurun.")
page()

h("4.2 Visualisasi data (lanjutan)",1)
fig("4_4_scatter","Gambar 4.4. Rasio murid/guru SMP dan kemiskinan.")
p("Sebaran titik menunjukkan karakteristik wilayah yang berbeda. Hubungan linear gabungan rasio murid/guru SMP dengan kemiskinan sangat kecil, r = -0,102. Rasio ini menggambarkan jumlah murid relatif terhadap guru dan tidak mengukur mutu pembelajaran maupun tingkat pendidikan penduduk.")
fig("4_5_heatmap","Gambar 4.5. Matriks kemiskinan tujuh wilayah dan tujuh tahun.")
p("Heatmap memperlihatkan konsistensi posisi Lingga pada tingkat kemiskinan yang relatif tinggi selama periode pengamatan. Pembacaan dilakukan bersama grafik tren agar tingkat saat ini dan perubahan sepanjang waktu tidak tertukar. Kelima grafik EDA memenuhi jumlah minimum visualisasi pada pedoman.")
page()

h("4.3 Analisis korelasi",1)
p("Koefisien Pearson dihitung pada 49 pasangan observasi wilayah-tahun. Nilai positif menunjukkan kecenderungan bergerak searah, sedangkan nilai negatif menunjukkan kecenderungan berlawanan arah. Besar absolut mendekati nol berarti hubungan linear gabungan kecil; hasil ini tidak menguji sebab-akibat atau membuktikan tidak adanya hubungan nonlinier.")
cor=D["correlation_target"]
table(["Indikator terhadap kemiskinan","Pearson r","Pembacaan deskriptif"],[
    ["Kepadatan penduduk",n(cor["Kepadatan_Penduduk_Sumber"]),"Negatif, mendekati nol"],
    ["SD per 10.000 penduduk",n(cor["Rasio_SD_10000"]),"Positif; paling besar dari fitur rasio ini"],
    ["Murid per guru SMP",n(cor["Rasio_Murid_Guru_SMP"]),"Negatif, mendekati nol"],
    ["Puskesmas per 10.000",n(cor["Rasio_Puskesmas_10000"]),"Dekat nol; sumber bermasalah"],
    ["RSU per 10.000",n(cor["Rasio_RSU_10000"]),"Dekat nol; asal data perlu ditelusuri"],
    ["Garis kemiskinan (rupiah)",n(cor["Garis_Kemiskinan_Maret_Rp"]),"Negatif, mendekati nol"],
    ["Jumlah penduduk (ribu)",n(cor["Jumlah_Penduduk_Ribu"]),"Negatif; hubungan gabungan"],
],[200,65,195])
small("Tabel 4.2. Korelasi Pearson. Tidak digunakan sebagai uji signifikansi.")
p("Korelasi SD per penduduk sebesar 0,428 tidak berarti menambah sekolah meningkatkan kemiskinan. Wilayah berpenduduk sedikit dapat memiliki rasio sekolah tinggi karena penyebaran permukiman, sekaligus memiliki karakteristik ekonomi berbeda. Penjelasan ini adalah hipotesis untuk ditelusuri, bukan hasil pengujian mekanisme.")
p("Data mencampur perbedaan antarwilayah dan perubahan dari tahun ke tahun. Korelasi gabungan dapat berbeda dari korelasi di dalam satu wilayah. Tidak dilakukan uji p-value yang menganggap seluruh baris independen. EDA seluruh periode juga tidak dipakai untuk memilih fitur berdasarkan skor testing; fitur utama mengikuti konfigurasi proyek yang sudah ada.")
h("4.4 Insight awal")
p("Pertama, kesenjangan tingkat kemiskinan masih terlihat pada akhir periode, meskipun beberapa wilayah membaik. Kedua, rasio fasilitas memberi konteks yang berbeda dari jumlah absolut, tetapi tidak cukup untuk mengukur akses atau mutu layanan. Ketiga, hubungan linear sederhana sebagian besar kecil sehingga model prediksi perlu dibandingkan dengan baseline.")
p("Keempat, terdapat 25 ketidaksesuaian total puskesmas terhadap jumlah rinciannya. Kolom tersebut dikeluarkan dari model utama. Rasio RSU tetap digunakan sebagai fitur eksploratif sesuai rancangan proyek, disertai analisis sensitivitas tanpa fitur kesehatan karena keterlacakan sumber kesehatan belum tuntas.")
page()

h("BAB 5 – Modeling",1)
h("5.1 Pemilihan algoritma")
p("Dua algoritma digunakan untuk menjawab dua pertanyaan berbeda. K-Means mengelompokkan observasi berdasarkan kemiripan karakteristik; regresi linear berganda memperkirakan persentase kemiskinan dari indikator numerik. Keduanya memenuhi persyaratan minimum dua algoritma. Skor keduanya tidak dibandingkan langsung karena tujuan dan metriknya berbeda.")
table(["Metode","Tujuan dan alasan","Batas"],[
    ["K-Means","Segmentasi numerik yang dapat dijelaskan melalui centroid; cocok sebagai model eksploratif sederhana.","Sensitif terhadap skala, fitur, pencilan, dan bentuk kelompok."],
    ["Regresi linear berganda","Model awal yang mudah ditelusuri melalui koefisien dan galat prediksi.","Hubungan diasumsikan aditif-linear; belum mengendalikan efek wilayah dan waktu."],
    ["PCA (pendukung)","Proyeksi dua dimensi untuk melihat hasil K-Means.","Tidak digunakan sebagai input clustering pada eksperimen ini."],
],[85,205,170])
p("Alternatif seperti Random Forest dapat memodelkan nonlinieritas, tetapi tidak diperlukan hanya untuk menambah kompleksitas pada 35 observasi training. Penelitian ini mengutamakan evaluasi yang jujur atas dua algoritma yang telah dirancang. Apabila dosen mensyaratkan perbandingan dua algoritma pada tugas prediksi yang sama, diperlukan eksperimen regresi pembanding tambahan; ketentuan yang tersedia menyebut minimum dua algoritma secara umum.")
table(["Variabel","K-Means","Regresi"],[
    ["Persentase kemiskinan Maret","Fitur","Target Y"],
    ["Kepadatan penduduk","Fitur","Prediktor X1"],
    ["Murid per guru SMP","Fitur","Prediktor X2"],
    ["RSU per 10.000 penduduk","Fitur eksploratif","Prediktor X3 eksploratif"],
    ["Wilayah dan tahun","Identitas hasil","Identitas dan pemisahan waktu"],
    ["Puskesmas per 10.000","Dikeluarkan","Dikeluarkan"],
],[240,110,110])
p("Rasio RSU = jumlah RSU / (penduduk dalam ribu × 1.000) × 10.000. Rasio murid/guru = jumlah murid SMP / jumlah guru SMP. Target dan turunan langsung target tidak dimasukkan sebagai prediktor agar tidak terjadi kebocoran informasi.")
page()

h("5.2 Training",1)
p("Untuk K-Means, empat fitur dinormalisasi Min-Max pada seluruh 49 observasi: z = (x - minimum)/(maksimum - minimum). Model dipasang untuk K=2, 3, dan 4. Seluruh periode digunakan karena tujuan eksperimen adalah segmentasi retrospektif terhadap data yang tersedia.")
p("Untuk regresi, data dipisah berdasarkan tahun terlebih dahulu. Training mencakup 2019–2023, sebanyak 35 observasi. Minimum dan maksimum prediktor hanya dihitung dari training. Regresi linear dipasang pada prediktor hasil transformasi tersebut. Scaler training yang sama diterapkan pada testing, sesuai prinsip pencegahan data leakage [5].")
h("5.3 Testing")
p("Testing regresi terdiri atas 14 observasi tahun 2024–2025. Model tidak dilatih ulang menggunakan target testing. Pemisahan ini menguji transfer ke tahun yang lebih baru pada tujuh wilayah yang sama, sehingga tidak mengukur kemampuan pada wilayah yang sama sekali baru.")
p("Prediktor berasal dari tahun yang sama dengan target kemiskinan. Karena tanggal rilis dan ketersediaan setiap indikator belum diverifikasi, eksperimen ini merupakan estimasi retrospektif bersyarat pada indikator tahun uji, bukan bukti ramalan yang dapat dibuat sebelum tahun tersebut berlangsung. Peramalan operasional membutuhkan fitur yang tersedia pada tanggal prediksi, misalnya fitur berlag.")
p("K-Means tidak memiliki label benar maupun testing berlabel dalam rancangan ini. Evaluasinya bersifat internal menggunakan Silhouette, inertia, ukuran cluster, serta kestabilan seed. Tidak dilaporkan accuracy, precision, recall, atau F1 karena tidak ada tugas klasifikasi berlabel.")
h("5.4 Parameter")
table(["Komponen","Pengaturan"],[
    ["K-Means","K = 2, 3, 4; init = k-means++; n_init = 20; random_state = 42"],
    ["K-Means (default sklearn 1.6.1)","max_iter = 300; tol = 0,0001; algorithm = lloyd"],
    ["Regresi linear","LinearRegression; fit_intercept = True; positive = False"],
    ["Normalisasi","MinMaxScaler, rentang 0–1; parameter regresi dari training saja"],
    ["PCA","2 komponen; hanya visualisasi; data empat fitur Min-Max"],
    ["Uji kestabilan","Seed 0, 1, 7, 21, 99; K terpilih dan n_init tetap"],
    ["Uji sensitivitas","Mengeluarkan RSU; bukan pemilihan ulang model dari testing"],
],[160,300])
p("K dipilih berdasarkan Silhouette tertinggi dalam rentang kandidat dengan pemeriksaan ukuran dan interpretasi kelompok. Elbow menjadi bukti pendamping. Tidak dilakukan pencarian parameter regresi berdasarkan hasil testing; hasil sensitivitas dilaporkan sebagai pemeriksaan tambahan.")
page()

h("5.5 Hasil model",1)
h("5.5.1 Hasil K-Means")
p("K=4 terpilih di antara kandidat K=2–4. Semua tahun dari suatu wilayah berada pada cluster yang sama pada hasil ini. Hal tersebut menunjukkan perbedaan antarwilayah lebih menonjol dalam segmentasi ini daripada perpindahan profil tahunan. Cluster adalah kelompok observasi, bukan peringkat pembangunan.")
table(["Cluster / anggota wilayah","n","Miskin (%)","Kepadatan","Murid/guru","RSU/10 rb"],[
    ["C0: Bintan, Karimun, Natuna","21","5,713","148,476","12,008","0,146"],
    ["C1: Batam, Tanjungpinang","14","6,579","1.419,500","18,152","0,130"],
    ["C2: Anambas","7","6,796","78,857","6,475","0,623"],
    ["C3: Lingga","7","12,154","44,857","11,196","0,201"],
],[160,30,65,75,65,65])
small("Tabel 5.1. Centroid dalam satuan asli; n adalah observasi wilayah-tahun.")
fig("5_1_pca","Gambar 5.1. Proyeksi PCA dari hasil K=4.")
p("Dua komponen menjelaskan 80,52% variasi fitur ternormalisasi (PC1 62,71%; PC2 17,81%). Sekitar 19,48% variasi tidak terlihat pada grafik dua dimensi. K-Means tetap dilatih pada empat fitur, sehingga jarak pada gambar merupakan penyederhanaan.")
p("C1 berciri kepadatan dan rasio murid/guru relatif tinggi. C2 memiliki rasio RSU per penduduk tertinggi dalam kelompok ini. C3 dicirikan kemiskinan tertinggi. C0 menggabungkan tiga wilayah dengan profil gabungan yang relatif berdekatan. Penamaan memakai karakteristik nyata, bukan label otomatis maju, sedang, atau tertinggal.")
page()

h("5.5.2 Hasil regresi linear",1)
p("Persamaan berikut memakai koefisien yang telah dikembalikan ke satuan asli. Y adalah kemiskinan dalam persen; X1 kepadatan (jiwa/km²), X2 murid per guru SMP, dan X3 RSU per 10.000 penduduk.")
p("Y prediksi = 9,665594 + 0,000200453 X1 - 0,135805 X2 - 2,528276 X3.")
p("Sebagai pembacaan model, tambahan 100 jiwa/km² berkaitan dengan perubahan prediksi sekitar +0,020 poin persentase ketika prediktor lain tetap. Tambahan satu murid per guru berkaitan dengan -0,136 poin, dan tambahan 0,1 RSU per 10.000 penduduk berkaitan dengan -0,253 poin. Koefisien ini tidak dapat digunakan untuk menyatakan dampak intervensi atau hubungan kausal.")
table(["Wilayah (2025)","Aktual (%)","Prediksi (%)","Residual (pp)"],[
    [short.get(x["Kabupaten_Kota"],x["Kabupaten_Kota"]),n(x["aktual"],2),
     n(x["prediksi"],3),n(x["residual"],3)]
    for x in D["regression"]["predictions"] if x["Tahun"]==2025
],[160,95,105,100])
small("Tabel 5.2. Prediksi testing tahun 2025. Residual = aktual - prediksi; seluruh 14 baris tersedia pada Lampiran A.")
p("Prediksi 2025 terkonsentrasi pada kisaran sekitar 6,95%–7,94%, sementara aktual 3,81%–9,12%. Model melebihkan kemiskinan wilayah dengan aktual rendah, seperti Batam dan Natuna, serta meremehkan Lingga. Pola ini membantu menjelaskan rendahnya kemampuan generalisasi model.")
h("5.5.3 Bukti implementasi")
p("Perhitungan memakai layanan preprocessing, clustering, dan regresi dalam backend proyek melalui skrip analisis laporan. Hasil disimpan sebagai JSON serta tabel CSV, kemudian divisualisasikan. Workbook sumber dibaca tanpa ditulis ulang. Skrip juga menambahkan baseline nilai 2023 dan analisis sensitivitas untuk kebutuhan evaluasi laporan.")
p("Versi eksekusi: Python "+D["versions"]["python"]+", pandas "+D["versions"]["pandas"]+
  ", NumPy "+D["versions"]["numpy"]+", scikit-learn "+D["versions"]["sklearn"]+
  ". Keberhasilan eksekusi analisis ini membuktikan keluaran perhitungan, bukan otomatis keberhasilan seluruh antarmuka web atau pengujian integrasinya.")
page()

h("BAB 6 – Evaluation",1)
h("6.1 Evaluasi clustering: Silhouette dan Elbow")
p("Silhouette mengukur kedekatan observasi dengan cluster sendiri dibandingkan cluster terdekat lainnya; rentangnya -1 sampai 1. Nilai lebih tinggi menunjukkan pemisahan internal lebih jelas pada fitur dan skala yang digunakan [4]. Inertia adalah jumlah kuadrat jarak ke centroid; nilainya cenderung turun ketika K bertambah.")
table(["K","Inertia / WCSS","Silhouette","Ukuran cluster"],[
    [e["k"],n(e["inertia"],4),n(e["silhouette"],4),", ".join(map(str,e["counts"].values()))]
    for e in D["clustering"]["evaluations"]
],[45,125,125,165])
fig("6_1_evaluasi_cluster","Gambar 6.1. Kurva Elbow dan perbandingan Silhouette.")
p("K=4 memiliki Silhouette 0,6310, lebih tinggi daripada K=3 (0,5760) dan K=2 (0,5369). Inertia turun dari 8,0139 menjadi 4,5098 lalu 2,3579. Hanya tiga kandidat diuji, sehingga titik siku tidak dapat dinyatakan tegas. Pemilihan K=4 terutama ditopang Silhouette dan interpretasi, bukan klaim optimum global.")
h("6.2 Kestabilan dan sensitivitas")
p("Pada lima seed tambahan, Adjusted Rand Index (ARI) terhadap hasil seed 42 sama dengan 1,000: pembagian anggota identik meskipun nomor label dapat berbeda. Namun dua cluster hanya mewakili masing-masing satu wilayah dengan tujuh tahun observasi; jumlah baris tersebut tidak berarti banyak wilayah independen.")
p("Setelah rasio RSU dihapus, kesesuaian anggota pada K=4 turun menjadi ARI 0,684. Artinya, hasil cukup peka terhadap fitur kesehatan. Uji seed memeriksa pengaruh inisialisasi; ia tidak membuktikan ketahanan terhadap perubahan data atau kualitas sumber.")
page()

h("6.3 Evaluasi regresi",1)
p("MAE = rerata |aktual - prediksi|. RMSE = akar rerata (aktual - prediksi)² dan memberi penalti lebih besar pada galat besar. R² = 1 - SSE/SST, dengan SST dihitung terhadap rerata aktual testing. MAE dan RMSE dinyatakan dalam poin persentase; nilai lebih kecil lebih baik. R² dapat negatif [6].")
metrics=[
    ("Regresi linear (3 fitur)",D["regression"]["metrics"]),
    ("Baseline rerata training",D["regression"]["baseline_metrics"]),
    ("Baseline nilai wilayah 2023",D["regression"]["baseline_2023_metrics"]),
    ("Sensitivitas tanpa RSU",D["sensitivity"]["regression_without_rsu"]["metrics"]),
]
table(["Model / pembanding","MAE (pp)","RMSE (pp)","R²"],[
    [name,n(m["mae"]),n(m["rmse"]),n(m["r2"])] for name,m in metrics
],[220,80,80,80])
small("Tabel 6.2. Evaluasi pada 14 observasi yang sama, 2024–2025.")
p("Baseline rerata memakai 7,432%, yaitu rerata target training, untuk seluruh observasi uji. Baseline wilayah memakai nilai tahun 2023 masing-masing wilayah, tetap sama untuk kedua tahun testing. Baseline ini tidak memakai aktual 2024 untuk memprediksi 2025, sehingga semua informasi pembanding berasal dari training.")
p("Regresi memperoleh MAE 2,013 dan RMSE 2,185, sedikit lebih buruk daripada baseline rerata training. Baseline wilayah jauh lebih baik, dengan MAE 0,854 dan RMSE 1,057. R² -0,760 menunjukkan regresi lebih buruk daripada prediksi konstan berdasarkan rerata aktual testing sebagai penyebut definisi R²; baseline rerata training pada tabel adalah pembanding terpisah yang bisa dibuat tanpa mengetahui target testing.")
fig("6_2_regresi","Gambar 6.2. Aktual versus prediksi dan residual testing.")
page()

h("6.4 Analisis galat dan keterbatasan evaluasi",1)
table(["Wilayah","MAE testing (pp)"],[
    [short.get(x["Kabupaten_Kota"],x["Kabupaten_Kota"]),n(x["absolute_error"])]
    for x in D["regression"]["region_errors"]
],[280,180])
small("Tabel 6.3. Rerata galat absolut berdasarkan dua tahun testing per wilayah.")
p("Galat terbesar terjadi pada Natuna (3,036 poin), Batam (2,646 poin), dan Bintan (2,568 poin). Galat terkecil terjadi pada Anambas (0,858 poin). Masing-masing nilai hanya berasal dari dua observasi, sehingga tidak cukup untuk menyimpulkan pola galat jangka panjang.")
p("Empat observasi uji berada di luar rentang training pada setidaknya satu prediktor: Bintan dan Anambas pada 2024 serta 2025. Transformasi Min-Max mempertahankan nilai di luar 0–1; tidak dilakukan clipping agar ekstrapolasi tetap terlihat.")
p("Mengeluarkan RSU memberi MAE 1,980 dan R² -0,668. Perbaikan tersebut belum mengatasi kelemahan model, dan tetap kalah dari baseline wilayah. Karena hasil ini diperiksa sesudah hasil utama, ia diperlakukan sebagai sensitivitas eksploratif, bukan bukti model baru telah lolos validasi independen.")
h("6.5 Keputusan kelayakan")
p("K-Means dapat dipakai untuk merangkum profil data yang tersedia, dengan menyertakan hasil sensitivitas dan catatan sumber. Regresi linear belum layak menjadi dasar estimasi kebijakan. Keputusan ini didasarkan pada performa testing dan baseline, bukan pada keindahan grafik atau kemudahan menjelaskan koefisien.")
p("Batas evaluasi meliputi sampel kecil, observasi panel berulang, satu holdout waktu, belum adanya validasi pada wilayah baru, dan perbedaan waktu pengukuran antartema. Data kemiskinan memakai Maret, sementara pendidikan memakai tahun akhir ajaran. Selain itu, indikator layanan hanya menghitung fasilitas atau rasio dan tidak mengukur kapasitas, mutu, jarak, maupun biaya akses.")
p("Tahap lanjutan sebaiknya menggunakan validasi bergulir dengan semua baris dari tahun yang sama berada pada fold yang sama, memasang scaler di dalam tiap training fold, dan menyisakan periode evaluasi baru. Membagi data panel secara acak dapat mencampurkan tahun dan menghasilkan evaluasi yang tidak sesuai tujuan prediksi ke depan.")
page()

h("BAB 7 – Insight dan Kesimpulan",1)
h("7.1 Apa yang dapat dipelajari dari data?")
p("Kesenjangan tingkat kemiskinan masih terlihat pada akhir periode. Lingga turun dari 12,88% pada 2019 menjadi 9,12% pada 2025, tetapi tetap memiliki persentase tertinggi pada 2025. Pencapaian penurunan dan posisi relatif merupakan dua informasi berbeda yang perlu dibahas bersama.")
table(["Wilayah","2019 (%)","2025 (%)","Perubahan (pp)"],[
    [short.get(x["Kabupaten_Kota"],x["Kabupaten_Kota"]),n(x["2019"],2),
     n(x["2025"],2),n(x["perubahan_pp"],2)] for x in D["change"]
],[175,90,90,105])
small("Tabel 7.1. Perubahan antartitik waktu. Nilai negatif menunjukkan penurunan.")
p("Karakteristik wilayah tidak dapat dirangkum hanya oleh kemiskinan. Batam dan Tanjungpinang masuk cluster yang sama karena kombinasi kepadatan dan rasio murid/guru, meskipun tingkat kemiskinannya berbeda. Anambas memiliki rasio RSU per penduduk tinggi pada workbook, tetapi angka tersebut belum menunjukkan bahwa penduduk menikmati akses layanan yang lebih baik.")
p("Korelasi rendah dan hasil regresi yang lemah memperlihatkan bahwa fitur terpilih belum cukup menjelaskan variasi kemiskinan pada tahun uji. Kinerja baseline wilayah yang lebih baik menunjukkan nilai historis kemiskinan merupakan pembanding yang relevan. Hasil ini tidak membuktikan pendidikan atau kesehatan tidak berhubungan dengan kemiskinan.")
h("7.2 Implikasi hasil analisis")
p("Kelompok dengan profil berbeda memerlukan penelusuran kebutuhan yang berbeda. Profil kemiskinan tinggi dapat menjadi titik awal pemilihan wilayah untuk kajian lebih lanjut. Profil kepadatan tinggi dapat menjadi dasar memeriksa beban layanan. Keduanya tetap memerlukan data tambahan sebelum menjadi keputusan alokasi anggaran.")
p("Tidak ada peringkat pembangunan resmi yang dihasilkan. Nomor cluster bersifat arbitrer, dan keanggotaan dipengaruhi pilihan fitur serta normalisasi. Penelitian ini memberi peta awal untuk diskusi, bukan dasar tunggal penetapan daerah maju atau tertinggal.")
page()

h("7.3 Rekomendasi",1)
p("Pertama, kelompok perlu memprioritaskan verifikasi sumber. Telusuri 25 ketidaksesuaian puskesmas, definisi total dan rincian, serta asal angka RSU. Simpan URL tabel resmi, instansi, periode, tanggal unduh, satuan, dan aturan penggabungan. Jika kesesuaian dengan Satu Data diwajibkan, hubungkan data dengan entri katalog yang tepat atau minta klarifikasi dosen; jangan menambahkan URL yang belum diperiksa.")
p("Kedua, Lingga dapat diprioritaskan untuk kajian faktor kemiskinan lanjutan karena tetap tertinggi pada 2025. Kajian tersebut sebaiknya menambahkan kondisi pekerjaan, pengeluaran, transportasi, dan akses layanan. Temuan saat ini belum menentukan program intervensi tertentu yang pasti efektif.")
p("Ketiga, pada Batam dan Tanjungpinang, periksa distribusi murid dan guru per sekolah serta kapasitas layanan. Rasio agregat yang tinggi belum membuktikan kekurangan guru di setiap sekolah. Pada wilayah kepulauan, lengkapi rasio fasilitas dengan waktu tempuh, kapasitas tempat tidur, tenaga kesehatan, serta keterhubungan antarpulau.")
p("Keempat, pertahankan baseline nilai kemiskinan terakhir pada pengembangan model. Tambahkan fitur historis yang tersedia sebelum waktu prediksi, lakukan validasi berdasarkan blok tahun, dan bandingkan model baru dengan baseline pada data uji yang belum dipakai untuk memilih model. Penambahan algoritma saja tidak menjamin perbaikan.")
p("Kelima, gunakan dashboard untuk menunjukkan indikator asli, periode, centroid, galat, dan keterbatasan sumber. Tampilkan skor regresi apa adanya dan hindari tombol atau narasi yang menyebut hasil ini sebagai ramalan operasional yang sudah andal.")
h("7.4 Kesimpulan")
p("Analisis 49 observasi wilayah-tahun menghasilkan lima visualisasi EDA dan menunjukkan variasi karakteristik antarwilayah. K-Means memilih empat cluster dari kandidat K=2–4 dengan Silhouette 0,631. Pembagian stabil terhadap lima seed tambahan, tetapi berubah ketika fitur RSU dikeluarkan.")
p("Regresi linear berganda pada training 2019–2023 dan testing 2024–2025 menghasilkan MAE 2,013 poin persentase, RMSE 2,185 poin, dan R² -0,760. Kinerjanya lebih rendah daripada baseline rerata training maupun baseline nilai wilayah 2023. Dengan demikian, model ini belum memberikan manfaat prediksi dibandingkan pembanding sederhana.")
p("Kontribusi utama proyek adalah penyajian profil wilayah, pembuktian batas kemampuan model, dan rekomendasi perbaikan data serta evaluasi. Kesimpulan substantif tetap bersyarat pada kualitas workbook dan perlu diperkuat dengan penelusuran sumber resmi.")
page()

h("Lampiran A – Prediksi testing lengkap",1)
table(["Wilayah","Tahun","Aktual","Prediksi","Residual","Baseline 2023"],[
    [short.get(x["Kabupaten_Kota"],x["Kabupaten_Kota"]),x["Tahun"],
     n(x["aktual"],2),n(x["prediksi"]),n(x["residual"]),n(x["baseline_2023"],2)]
    for x in D["regression"]["predictions"]
],[120,45,65,75,75,80])
small("Aktual, prediksi, dan baseline dalam persen. Residual dalam poin persentase.")
h("Lampiran B – Reproduksibilitas")
p("Dari root proyek, jalankan backend\\.venv\\Scripts\\python.exe scripts\\analyze_chapters_4_7.py untuk menghitung ulang analisis, kemudian scripts\\plot_chapters_4_7.py dengan interpreter yang sama untuk membuat grafik. Skrip laporan scripts\\build_chapters_4_7.py memerlukan reportlab pada interpreter yang digunakan.")
p("Hasil lengkap disimpan di output/project2/analysis_results.json, prediksi_testing.csv, anggota_cluster.csv, dan data_analisis.csv. Grafik berada di subfolder figures. Paket visualisasi yang digunakan adalah matplotlib 3.10.7. Data sumber tidak diganti, dikoreksi otomatis, atau ditambah dengan observasi sintetis.")
small("SHA-256 workbook sumber: "+D["sha256"])
p("Pemeriksaan skrip mencakup 49 baris, kunci wilayah-tahun unik, kelengkapan fitur, serta hash sumber tetap sama setelah eksekusi. Hasil laporan berasal dari eksekusi analisis langsung. Pengujian UI, instalasi frontend, dan demonstrasi browser merupakan bukti terpisah yang tidak diklaim oleh laporan ini.")
page()

h("Lampiran C – Pemetaan rubrik Project 2",1)
table(["Komponen","Bobot","Bukti pada laporan / demonstrasi"],[
    ["Pemilihan metode/model","15%","5.1: pertanyaan, dua algoritma, alasan dan batas"],
    ["Implementasi","20%","5.2–5.5 dan Lampiran B: input, preprocessing, parameter, keluaran yang dapat diulang"],
    ["Evaluasi model","20%","BAB 6: Silhouette, Elbow, MAE, RMSE, R², baseline, sensitivitas"],
    ["Interpretasi hasil","20%","4.4, 5.5, 6.4, 7.1–7.2: makna hasil dan batas inferensi"],
    ["Rekomendasi","10%","7.3: tindakan berdasarkan temuan, kebutuhan verifikasi dan validasi"],
    ["Presentasi","15%","Alur di bawah; penyampaian dan demonstrasi tetap dilakukan kelompok"],
],[125,45,290])
p("Pemetaan menunjukkan bukti yang disiapkan, bukan jaminan nilai. Komponen presentasi menilai penyampaian kelompok; menuliskan alur saja tidak menggantikan presentasi aktual.")
h("Alur presentasi yang disarankan (10–12 menit)")
table(["Bagian","Pesan utama","Waktu"],[
    ["Masalah dan data","7 wilayah × 7 tahun; kebutuhan memahami kesenjangan","1 menit"],
    ["EDA","Tren, peringkat 2025, dan hubungan pendidikan–kemiskinan","2 menit"],
    ["Metode","Alasan K-Means dan regresi; split waktu dan normalisasi","2 menit"],
    ["Hasil cluster","K=4, centroid, Silhouette, dan batas interpretasi","2 menit"],
    ["Hasil regresi","Tunjukkan model kalah dari baseline dan jelaskan artinya","2 menit"],
    ["Rekomendasi dan demo","Bukti sumber, perbaikan model, ekspor hasil; simpulan","1–3 menit"],
],[110,290,60])
p("Siapkan jawaban untuk: mengapa tidak memakai accuracy; mengapa target tidak menjadi X regresi; mengapa R² negatif tetap dilaporkan; mengapa cluster bukan peringkat; dan mengapa prediksi tahun yang sama belum menjadi ramalan. Demonstrasikan satu alur dari dataset sampai keluaran, dengan parameter yang sama seperti laporan.")
page()

h("Daftar sumber",1)
p("[1] Kelompok 7. Data_Sains_Kepri_2019_2025 (12).xlsx, sheet Master_Integrasi. Berkas lokal yang digunakan untuk seluruh perhitungan; 49 baris dan 33 kolom sumber. Asal publikasi resmi perlu dilengkapi dari catatan pengumpulan.")
p("[2] Kelompok 7. Laporan Project 1.pdf. Bagian 1–3, definisi variabel, unit observasi, rekayasa fitur, dan catatan kualitas data. Pembacaan dilakukan dari ekstraksi teks yang tersedia dalam proyek.")
p("[3] Project Data Sains.pdf. Pedoman tugas: BAB 4, minimal lima visualisasi, minimum dua algoritma machine learning, BAB 5–7, dan rubrik Project 2. Dokumen diberikan pengguna.")
p("[4] Scikit-learn. Selecting the number of clusters with silhouette analysis on KMeans clustering. https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html")
p("[5] Scikit-learn. Common pitfalls and recommended practices. https://scikit-learn.org/1.8/common_pitfalls.html")
p("[6] Scikit-learn. Metrics and scoring: quantifying the quality of predictions. https://scikit-learn.org/1.8/modules/model_evaluation.html")
small("Dokumentasi metode diakses pada 20 Oktober 2026. Versi perangkat lunak eksekusi dicatat terpisah pada BAB 5; versi dokumentasi tidak dianggap sebagai versi yang terpasang.")
h("Hal yang masih perlu dilengkapi kelompok")
p("Lengkapi URL dataset resmi dan bukti keterlacakan sumber; selesaikan audit nilai kesehatan; periksa kesesuaian sumber dengan instruksi Satu Data; gabungkan dokumen ini dengan BAB 1–3 serta perbarui daftar isi dan penomoran; lalu lakukan presentasi dan demonstrasi aktual. Hasil model pada laporan sudah dihitung, sedangkan verifikasi sumber tersebut tetap terbuka.")

def footer(canvas,doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#cccccc"))
    canvas.line(50,42,545,42)
    canvas.setFont("Helvetica",8)
    canvas.drawString(50,29,"Kelompok 7 | Analisis pembangunan Kepulauan Riau")
    canvas.drawRightString(545,29,str(doc.page))
    canvas.restoreState()
doc=SimpleDocTemplate(str(OUT/"Laporan_BAB_4_sampai_7.pdf"),
    pagesize=(595.28,841.89),rightMargin=62,leftMargin=62,topMargin=46,bottomMargin=57,
    title="Laporan Data Sains BAB 4–7",author="Kelompok 7")
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(OUT/"Laporan_BAB_4_sampai_7.md").write_text("\n".join(md),encoding="utf-8")
print("Built PDF and Markdown")
