import pandas as pd
import matplotlib
matplotlib.use("Agg")  # supaya bisa jalan tanpa perlu tampilan layar aktif
import matplotlib.pyplot as plt
import os

# ==== KONFIGURASI ====
# Ganti nama file ini kalau rentang tanggal kamu berbeda
FILES = {
    "GAP": "gap_events_2024-01-01_to_2024-01-07.csv",
    "LOITERING": "loitering_events_2024-01-01_to_2024-01-07.csv",
    "ENCOUNTER": "encounter_events_2024-01-01_to_2024-01-07.csv",
}

OUTPUT_FOLDER = "eda_output"


def load_data():
    """Baca ketiga file CSV, kembalikan sebagai dictionary dataframe."""
    data = {}
    for name, filename in FILES.items():
        if not os.path.exists(filename):
            print(f"⚠️  File tidak ditemukan: {filename} (skip)")
            continue
        data[name] = pd.read_csv(filename)
        print(f"✅ {name}: {data[name].shape[0]} baris, {data[name].shape[1]} kolom")
    return data


def print_basic_summary(data: dict):
    """Cetak ringkasan dasar tiap dataset: jumlah baris, missing value, dsb."""
    print("\n" + "=" * 60)
    print("RINGKASAN DASAR")
    print("=" * 60)

    for name, df in data.items():
        print(f"\n--- {name} ---")
        print(f"Jumlah baris: {len(df)}")
        print(f"Jumlah kolom: {len(df.columns)}")

        missing = df.isna().mean().sort_values(ascending=False)
        missing = missing[missing > 0]
        if len(missing) > 0:
            print("Kolom dengan missing value terbanyak:")
            print(missing.head(5).apply(lambda x: f"{x:.1%}"))
        else:
            print("Tidak ada missing value signifikan.")


def print_vessel_flag_summary(data: dict):
    """Cetak top 5 negara bendera kapal per dataset."""
    print("\n" + "=" * 60)
    print("TOP 5 NEGARA BENDERA KAPAL (vessel.flag)")
    print("=" * 60)

    for name, df in data.items():
        if "vessel.flag" in df.columns:
            print(f"\n--- {name} ---")
            print(df["vessel.flag"].value_counts().head(5))


def print_specific_stats(data: dict):
    """Cetak statistik spesifik per jenis anomali."""
    print("\n" + "=" * 60)
    print("STATISTIK SPESIFIK PER JENIS ANOMALI")
    print("=" * 60)

    if "GAP" in data:
        df = data["GAP"]
        print("\n--- GAP ---")
        if "gap.durationHours" in df.columns:
            print("Durasi gap (jam):")
            print(df["gap.durationHours"].describe())
        if "gap.intentionalDisabling" in df.columns:
            print("\nIntentional disabling:")
            print(df["gap.intentionalDisabling"].value_counts())

    if "LOITERING" in data:
        df = data["LOITERING"]
        print("\n--- LOITERING ---")
        if "loitering.totalTimeHours" in df.columns:
            print("Total waktu loitering (jam):")
            print(df["loitering.totalTimeHours"].describe())
        if "loitering.averageDistanceFromShoreKm" in df.columns:
            print("\nJarak rata-rata dari pantai (km):")
            print(df["loitering.averageDistanceFromShoreKm"].describe())

    if "ENCOUNTER" in data:
        df = data["ENCOUNTER"]
        print("\n--- ENCOUNTER ---")
        if "encounter.potentialRisk" in df.columns:
            print("Potential risk:")
            print(df["encounter.potentialRisk"].value_counts())
        if "encounter.type" in df.columns:
            print("\nTipe encounter:")
            print(df["encounter.type"].value_counts())


def find_suspicious_vessels(data: dict):
    """Cari kapal (vessel.id) yang muncul di lebih dari 1 jenis anomali - pola mencurigakan."""
    print("\n" + "=" * 60)
    print("KAPAL YANG MUNCUL DI LEBIH DARI 1 JENIS ANOMALI")
    print("=" * 60)

    vessel_sets = {}
    for name, df in data.items():
        col = "vessel.id"
        if col in df.columns:
            vessel_sets[name] = set(df[col].dropna().unique())

    names = list(vessel_sets.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            overlap = vessel_sets[names[i]] & vessel_sets[names[j]]
            print(f"\n{names[i]} ∩ {names[j]}: {len(overlap)} kapal yang sama")

    if len(names) == 3:
        triple_overlap = vessel_sets[names[0]] & vessel_sets[names[1]] & vessel_sets[names[2]]
        print(f"\n⚠️  Kapal yang muncul di SEMUA 3 jenis anomali: {len(triple_overlap)}")
        if len(triple_overlap) > 0:
            print("ID kapal:", list(triple_overlap)[:10], "..." if len(triple_overlap) > 10 else "")


def make_charts(data: dict):
    """Buat beberapa grafik dan simpan sebagai file PNG."""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print("\n" + "=" * 60)
    print("MEMBUAT GRAFIK")
    print("=" * 60)

    # Chart 1: Top 10 negara bendera per jenis anomali
    fig, axes = plt.subplots(1, len(data), figsize=(6 * len(data), 5))
    if len(data) == 1:
        axes = [axes]

    for ax, (name, df) in zip(axes, data.items()):
        if "vessel.flag" in df.columns:
            top_flags = df["vessel.flag"].value_counts().head(10)
            ax.barh(top_flags.index[::-1], top_flags.values[::-1], color="steelblue")
            ax.set_title(f"Top 10 Negara Bendera - {name}")
            ax.set_xlabel("Jumlah Event")

    plt.tight_layout()
    chart1_path = os.path.join(OUTPUT_FOLDER, "01_top_negara_bendera.png")
    plt.savefig(chart1_path, dpi=120)
    plt.close()
    print(f"✅ Disimpan: {chart1_path}")

    # Chart 2: Distribusi durasi GAP (kalau ada)
    if "GAP" in data and "gap.durationHours" in data["GAP"].columns:
        plt.figure(figsize=(8, 5))
        plt.hist(data["GAP"]["gap.durationHours"], bins=30, color="tomato", edgecolor="black")
        plt.title("Distribusi Durasi AIS GAP (jam)")
        plt.xlabel("Durasi (jam)")
        plt.ylabel("Jumlah Event")
        plt.tight_layout()
        chart2_path = os.path.join(OUTPUT_FOLDER, "02_distribusi_durasi_gap.png")
        plt.savefig(chart2_path, dpi=120)
        plt.close()
        print(f"✅ Disimpan: {chart2_path}")

    # Chart 3: Distribusi total waktu LOITERING (kalau ada)
    if "LOITERING" in data and "loitering.totalTimeHours" in data["LOITERING"].columns:
        plt.figure(figsize=(8, 5))
        plt.hist(data["LOITERING"]["loitering.totalTimeHours"], bins=30, color="orange", edgecolor="black")
        plt.title("Distribusi Total Waktu Loitering (jam)")
        plt.xlabel("Total Waktu (jam)")
        plt.ylabel("Jumlah Event")
        plt.tight_layout()
        chart3_path = os.path.join(OUTPUT_FOLDER, "03_distribusi_waktu_loitering.png")
        plt.savefig(chart3_path, dpi=120)
        plt.close()
        print(f"✅ Disimpan: {chart3_path}")

    # Chart 4: Encounter type breakdown (kalau ada)
    if "ENCOUNTER" in data and "encounter.type" in data["ENCOUNTER"].columns:
        plt.figure(figsize=(7, 5))
        counts = data["ENCOUNTER"]["encounter.type"].value_counts()
        plt.bar(counts.index, counts.values, color="purple")
        plt.title("Tipe Encounter")
        plt.ylabel("Jumlah Event")
        plt.xticks(rotation=20)
        plt.tight_layout()
        chart4_path = os.path.join(OUTPUT_FOLDER, "04_tipe_encounter.png")
        plt.savefig(chart4_path, dpi=120)
        plt.close()
        print(f"✅ Disimpan: {chart4_path}")

    print(f"\nSemua grafik tersimpan di folder: {OUTPUT_FOLDER}/")


def main():
    print("Memuat data...\n")
    data = load_data()

    if not data:
        print("\n❌ Tidak ada file yang berhasil dimuat. Cek nama file di bagian FILES.")
        return

    print_basic_summary(data)
    print_vessel_flag_summary(data)
    print_specific_stats(data)
    find_suspicious_vessels(data)
    make_charts(data)

    print("\n" + "=" * 60)
    print("SELESAI! Cek folder 'eda_output' untuk grafik-grafiknya.")
    print("=" * 60)


if __name__ == "__main__":
    main()