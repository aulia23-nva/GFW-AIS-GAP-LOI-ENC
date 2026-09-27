import requests
import pandas as pd
import time
import folium

# ==== KONFIGURASI ====
TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtpZEtleSJ9.eyJkYXRhIjp7Im5hbWUiOiJPY2Vhbi1DcmltZS1Bbm9tYWx5LVJlc2VhcmNoIiwidXNlcklkIjo3MTcwOSwiYXBwbGljYXRpb25OYW1lIjoiT2NlYW4tQ3JpbWUtQW5vbWFseS1SZXNlYXJjaCIsImlkIjoxNDk5OSwidHlwZSI6InVzZXItYXBwbGljYXRpb24ifSwiaWF0IjoxNzkwMTk4MTU5LCJleHAiOjIxMDU1NTgxNTksImF1ZCI6ImdmdyIsImlzcyI6ImdmdyJ9.LvoPpx3pMWR5EZcxGC1hBDOfJP-U8g4WBQ-wQBj3Jph88csQ3JxGXUFFZ5bE494R2_w6R6Z0czOZCYwaAvJ1tYdlzhbhyOOYDiWnuqe075wnXDbbauw0gfmIPHU8qUDcv9m91hHrNUcRoQc53AwFZm-DmsSF3mDtmRA5RLIw9QBuF_rCHjj-Nbul1NR8UMR03MI34PmmMkoRwu1wVvx4sxJblGtf4uLrtowYDEvJTTSC1QvJ1N-HasfKeGCaC3_42VEHddoDR2x5GCchwLhVq0Bg7cLQMCBPafFdBjQq5awUuYuyq_hqwpRwq6L4if3HUHtGHcIfgGXXLAAN6trGF1srowRKKIRRMwglvcTnXC2LFre8sR9v9pfciDcuholOCMQPKGuSuOtdFl4HKaPy2ZYohiwQTE6nR0fdpeKQe_7Br4GkfeCGsF-iLs8pAYr8sR_Y4GAScYZxLC-b2ZW5MFJz05guhuKRfWgZNBQDKbBLAnY8AiQIXLzhcqO7Hn8j"

START_DATE = "2024-01-01"   # <-- (1-2 minggu) untuk testing
END_DATE = "2024-01-07"

BASE_URL = "https://gateway.api.globalfishingwatch.org/v3/events"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Jenis event yang mau diambil, dan nama dataset resminya di GFW v3
EVENT_TYPES = {
    "GAP": "public-global-gaps-events:latest",
    "LOITERING": "public-global-loitering-events:latest",
    "ENCOUNTER": "public-global-encounters-events:latest",
}

# Warna marker berbeda untuk tiap jenis anomali di peta
COLORS = {
    "GAP": "red",
    "LOITERING": "orange",
    "ENCOUNTER": "purple",
}


def fetch_events(event_type: str, dataset_name: str, start_date: str, end_date: str, max_events: int = 2000):
    """Ambil event untuk satu jenis, dengan pagination otomatis dan batas maksimal (supaya tidak kelamaan)."""
    all_events = []
    offset = 0
    limit = 50

    print(f"\n=== Mengambil data: {event_type} ===")

    while len(all_events) < max_events:
        params = {
            "datasets[0]": dataset_name,
            "start-date": start_date,
            "end-date": end_date,
            "limit": limit,
            "offset": offset,
        }

        response = requests.get(BASE_URL, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"Gagal request {event_type}: {response.status_code} - {response.text}")
            break

        data = response.json()
        entries = data.get("entries", [])

        if not entries:
            break

        all_events.extend(entries)
        print(f"  Terkumpul: {len(all_events)} event...")

        offset += limit
        time.sleep(0.5)

        if len(entries) < limit:
            break

    return all_events[:max_events]


def add_events_to_map(events, event_type, feature_group):
    """Tambahkan marker untuk setiap event ke peta."""
    count = 0
    for ev in events:
        try:
            lat = ev.get("position", {}).get("lat")
            lon = ev.get("position", {}).get("lon")

            if lat is None or lon is None:
                continue

            vessel_name = ev.get("vessel", {}).get("name", "Unknown")
            start_time = ev.get("start", "N/A")

            popup_text = f"""
            <b>Jenis:</b> {event_type}<br>
            <b>Kapal:</b> {vessel_name}<br>
            <b>Waktu:</b> {start_time}
            """

            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                popup=folium.Popup(popup_text, max_width=250),
                color=COLORS.get(event_type, "blue"),
                fill=True,
                fill_opacity=0.7,
            ).add_to(feature_group)

            count += 1
        except Exception:
            continue

    print(f"  {count} titik ditambahkan ke peta untuk {event_type}")


def main():
    # Peta dasar, pusat di titik 0,0 (bisa disesuaikan nanti)
    peta = folium.Map(location=[0, 0], zoom_start=2)
    folium.TileLayer(
       tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
       attr="Esri, HERE, Garmin, FAO, NOAA, USGS",
       name="Esri World Street Map",
   ).add_to(peta)        

    for event_type, dataset_name in EVENT_TYPES.items():
        events = fetch_events(event_type, dataset_name, START_DATE, END_DATE)

        if events:
            # Simpan CSV
            df = pd.json_normalize(events)
            filename = f"{event_type.lower()}_events_{START_DATE}_to_{END_DATE}.csv"
            df.to_csv(filename, index=False)
            print(f"✅ Disimpan: {filename} ({len(df)} baris)")

            # Tambahkan ke peta, dikelompokkan per jenis (bisa di-toggle on/off di peta)
            fg = folium.FeatureGroup(name=event_type)
            add_events_to_map(events, event_type, fg)
            fg.add_to(peta)
        else:
            print(f"⚠️  Tidak ada data {event_type} pada rentang tanggal ini.")

    folium.LayerControl().add_to(peta)

    peta_filename = f"map_anomali_{START_DATE}_to_{END_DATE}.html"
    peta.save(peta_filename)
    print(f"\n🗺️  Peta disimpan: {peta_filename}")
    print("Buka file itu di browser untuk melihat visualisasinya (bisa toggle on/off tiap jenis anomali).")

    print("\nSelesai!")


if __name__ == "__main__":
    main()