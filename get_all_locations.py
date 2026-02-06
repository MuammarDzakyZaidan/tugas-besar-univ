import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm # Untuk progress bar
import time

# --- KONFIGURASI ---
INPUT_FILE = 'data/data_univ_2000.csv' # Sesuaikan lokasi file kamu
OUTPUT_FILE = 'data_univ_full_coord.csv'
USER_AGENT = "univ_ranking_project_student_v2" # Nama user agent unik

# 1. BACA DATA
try:
    df = pd.read_csv(INPUT_FILE)
    print(f"✅ Berhasil membaca {len(df)} data universitas.")
except FileNotFoundError:
    print(f"❌ Error: File {INPUT_FILE} tidak ditemukan.")
    exit()

# Siapkan kolom baru jika belum ada
if 'lat' not in df.columns:
    df['lat'] = None
    df['lon'] = None

# 2. PERSIAPAN GEOCODER
geolocator = Nominatim(user_agent=USER_AGENT)
# Jeda 1.2 detik agar aman dari blokir
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.2) 

print("🚀 Memulai pencarian koordinat untuk SEMUA data...")
print("☕ Proses ini akan memakan waktu sekitar 40-50 menit. Jangan tutup terminal.")

# 3. LOOPING DENGAN PROGRESS BAR
# tqdm akan memunculkan bar loading
for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Mencari Lokasi"):
    
    # Hanya cari jika lat/lon masih kosong (biar bisa dilanjutkan kalau putus)
    if pd.isna(row['lat']):
        try:
            # Cari: "Nama Univ, Negara"
            query = f"{row['Universitas']}, {row['Negara']}"
            location = geolocator.geocode(query, timeout=10)
            
            if location:
                df.at[index, 'lat'] = location.latitude
                df.at[index, 'lon'] = location.longitude
            else:
                # Opsi 2: Cari Nama Univ saja jika kombinasi negara gagal
                location = geolocator.geocode(row['Universitas'], timeout=10)
                if location:
                    df.at[index, 'lat'] = location.latitude
                    df.at[index, 'lon'] = location.longitude
                    
        except Exception as e:
            # Kalau error (timeout dll), skip dulu
            continue

    # 4. FITUR AUTO-SAVE (Setiap 50 data tersimpan)
    if index % 50 == 0:
        df.to_csv(OUTPUT_FILE, index=False)

# 5. SIMPAN HASIL AKHIR
# Hapus data yang tetap tidak ketemu lokasinya
df_final = df.dropna(subset=['lat', 'lon'])
df_final.to_csv(OUTPUT_FILE, index=False)

print("\n" + "="*50)
print(f"🎉 SELESAI! Data tersimpan di: {OUTPUT_FILE}")
print(f"Total data awal: {len(df)}")
print(f"Total data dengan lokasi akurat: {len(df_final)}")
print("Sekarang gunakan file baru ini di app_univ.py kamu.")