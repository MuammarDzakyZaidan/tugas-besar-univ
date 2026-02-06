import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------------
# KONFIGURASI HALAMAN
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Universitas Dunia",
    page_icon="",
    layout="wide"
)

# ------------------------------------------------------------------
# 1. LOAD DATASET BARU
# ------------------------------------------------------------------
# Pastikan file 'data_univ_full_coord.csv' sudah di-upload ke GitHub/Hugging Face
try:
    # Coba baca dari folder data (jika struktur folder 'data/')
    df = pd.read_csv('data/data_univ_full_coord.csv')
except FileNotFoundError:
    try:
        # Coba baca dari folder root (jika sejajar dengan app.py)
        df = pd.read_csv('data_univ_full_coord.csv')
    except FileNotFoundError:
        st.error("File CSV tidak ditemukan! Pastikan kamu sudah upload file 'data_univ_full_coord.csv'.")
        st.stop()

# ------------------------------------------------------------------
# 2. JUDUL DASHBOARD
# ------------------------------------------------------------------
st.title("Dashboard Pemeringkatan Universitas Dunia")
st.markdown("Analisis sebaran dan kualitas universitas top dunia berdasarkan CWUR")
st.markdown("---")

# ------------------------------------------------------------------
# 3. SIDEBAR (FILTER)
# ------------------------------------------------------------------
st.sidebar.header("Filter Data")

# Filter Negara
list_negara = ['Semua Negara'] + list(df['Negara'].unique())
pilih_negara = st.sidebar.selectbox("Pilih Negara:", list_negara)

# Filter Skor
min_score = int(df['Score'].min())
max_score = int(df['Score'].max())
score_range = st.sidebar.slider("Rentang Skor Kualitas:", min_score, max_score, (min_score, max_score))

# Terapkan Filter
if pilih_negara != 'Semua Negara':
    df_filtered = df[df['Negara'] == pilih_negara]
else:
    df_filtered = df

df_filtered = df_filtered[(df_filtered['Score'] >= score_range[0]) & (df_filtered['Score'] <= score_range[1])]

# Tampilkan Statistik Ringkas di Sidebar
st.sidebar.markdown("---")
st.sidebar.metric("Total Universitas", len(df_filtered))
st.sidebar.metric("Rata-rata Skor", f"{df_filtered['Score'].mean():.2f}")

# ------------------------------------------------------------------
# 4. VISUALISASI LAYAR 1: GRAFIK RINGKASAN
# ------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Negara dengan Univ Terbanyak")
    # Hitung jumlah univ per negara
    count_per_country = df_filtered['Negara'].value_counts().head(10).reset_index()
    count_per_country.columns = ['Negara', 'Jumlah']
    
    fig_bar = px.bar(
        count_per_country, 
        x='Jumlah', 
        y='Negara', 
        orientation='h',
        color='Jumlah',
        color_continuous_scale='Viridis'
    )
    # Membalik urutan agar yang terbanyak di atas
    fig_bar.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("Distribusi Skor Kualitas")
    fig_hist = px.histogram(
        df_filtered, 
        x="Score", 
        nbins=20, 
        color_discrete_sequence=['#ff4b4b']
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ------------------------------------------------------------------
# 5. VISUALISASI LAYAR 2: PETA SEBARAN (REAL COORDINATE)
# ------------------------------------------------------------------
st.markdown("---")
st.subheader("Peta Sebaran Universitas")

# Pastikan hanya memplot data yang punya koordinat lengkap
# Agar peta tidak error karena nilai kosong (NaN)
map_data = df_filtered.dropna(subset=['lat', 'lon'])

if not map_data.empty:
    fig_map = px.scatter_mapbox(
        map_data,
        lat="lat",
        lon="lon",
        hover_name="Universitas",
        hover_data={"Negara": True, "Rank": True, "Score": True, "lat": False, "lon": False},
        color="Negara",  # Warna titik berdasarkan negara
        zoom=1,
        height=600,
        size="Score",    # Ukuran titik berdasarkan skor (opsional, bisa dihapus jika terlalu ramai)
        size_max=15
    )

    # Menggunakan style OpenStreetMap (Gratis & Detail)
    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Data koordinat tidak ditemukan untuk filter yang dipilih.")

# ------------------------------------------------------------------
# 6. VISUALISASI LAYAR 3: TABEL DATA
# ------------------------------------------------------------------
st.markdown("---")
st.subheader("Tabel Data Detail Universitas")

search_term = st.text_input("Cari Universitas atau Negara:", "")

if search_term:
    # Filter tabel berdasarkan pencarian text
    df_display = df_filtered[
        df_filtered['Universitas'].str.contains(search_term, case=False) | 
        df_filtered['Negara'].str.contains(search_term, case=False)
    ]
else:
    df_display = df_filtered

# --- BAGIAN LOGIKA PENOMORAN BARU ---
# 1. Pilih kolom yang mau ditampilkan saja
tabel_final = df_display[['Rank', 'Universitas', 'Negara', 'Score', 'lat', 'lon']].copy()

# 2. Reset Index agar urut dari 0 lagi, lalu tambah 1 agar mulai dari angka 1
tabel_final.reset_index(drop=True, inplace=True)
tabel_final.index = tabel_final.index + 1

# 3. Tampilkan tabel
# Note: Kita menghapus 'hide_index=True' agar nomornya muncul di paling kiri
st.dataframe(
    tabel_final,
    use_container_width=True
)