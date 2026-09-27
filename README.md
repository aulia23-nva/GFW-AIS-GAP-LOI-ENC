# Ocean Crime Anomaly Detection — GFW Dataset Pipeline

Pipeline untuk mengambil, memvisualisasikan, dan menganalisis data anomali maritim (AIS GAP, Loitering, Encounter) dari **Global Fishing Watch (GFW) Events API**, sebagai dukungan riset deteksi pola *Illegal, Unreported, and Unregulated (IUU) Fishing* / kejahatan laut.

## Tentang Proyek

Proyek ini terdiri dari 2 script utama:

1. **`fetch_gfw_data.py`** — Mengambil data event anomali dari GFW Events API, menyimpannya sebagai CSV, dan memvisualisasikan lokasinya di peta interaktif (HTML).
2. **`eda_gfw_data.py`** — Melakukan Exploratory Data Analysis (EDA) terhadap CSV hasil pengambilan data: ringkasan statistik, deteksi kapal dengan pola mencurigakan (muncul di >1 jenis anomali), dan visualisasi grafik.

## Jenis Anomali

| Jenis | Deskripsi | Dataset GFW |
|---|---|---|
| **GAP** | Celah transmisi AIS yang tidak dapat dijelaskan, indikasi kemungkinan mematikan sistem AIS secara sengaja | `public-global-gaps-events:latest` |
| **LOITERING** | Kapal bergerak sangat lambat (<2 knot) jauh dari pantai (≥20 mil laut), indikasi potensi transshipment | `public-global-loitering-events:latest` |
| **ENCOUNTER** | Dua kapal bertemu di laut lepas, indikasi potensi transfer muatan/transshipment | `public-global-encounters-events:latest` |

> Catatan: proyek ini fokus pada 3 dari 5 anomali riset (GAP, Loitering, Encounter) yang tersedia langsung lewat GFW Events API. Spoofing dan pelanggaran zona terlarang (unauthorized zone entry) memerlukan sumber data/akses tambahan di luar scope script ini.

## Output

- **CSV per jenis anomali** — data mentah untuk analisis lanjutan
- **Peta interaktif (HTML)** — visualisasi lokasi semua event, bisa toggle on/off per jenis anomali
  <img width="1898" height="903" alt="image" src="https://github.com/user-attachments/assets/16808c25-58bd-4511-82c6-c0bda5048f18" />
  <img width="1906" height="906" alt="image" src="https://github.com/user-attachments/assets/e1110feb-f9c1-40cf-b842-ebb833ba2cca" />
- **Grafik EDA (PNG)** — distribusi durasi, top negara bendera kapal, tipe encounter
  <img width="2160" height="600" alt="image" src="https://github.com/user-attachments/assets/b69fb05c-e200-4d74-ac4e-92621a7f0ecb" />
  <img width="960" height="600" alt="image" src="https://github.com/user-attachments/assets/0a66c90e-bedc-48e9-95cd-53cdc73a8adc" />
  <img width="960" height="600" alt="image" src="https://github.com/user-attachments/assets/e63f3757-e1b8-46a8-a793-4e936eaad8cf" />
  <img width="840" height="600" alt="image" src="https://github.com/user-attachments/assets/c4a251b6-7beb-4a19-83ed-8d0dfc2cd1fa" />

- **Daftar kapal mencurigakan** — kapal yang muncul di lebih dari satu jenis anomali 

## Catatan & Batasan

- Script `fetch_gfw_data.py` membatasi maksimal **2000 event per jenis** (`max_events`) untuk menghindari waktu proses yang terlalu lama. Untuk riset dengan cakupan lebih luas, nilai ini perlu dinaikkan (dengan konsekuensi waktu proses lebih lama).
- Tile peta menggunakan **Esri World Street Map** (gratis, tanpa API key) karena OpenStreetMap langsung membatasi akses otomatis dari aplikasi/file lokal.
- Data GFW mencakup aktivitas kapal secara umum — tidak semua event (terutama GAP dan Loitering) otomatis berarti aktivitas ilegal. Diperlukan filtering/investigasi lanjutan sebelum menyimpulkan suatu event sebagai indikasi kejahatan laut.

## Sumber Data

[Global Fishing Watch](https://globalfishingwatch.org) — API resmi untuk data aktivitas kapal berbasis AIS, digunakan sesuai [Terms of Use](https://globalfishingwatch.org/our-apis) mereka.
