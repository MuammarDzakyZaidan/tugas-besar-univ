import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Global University Ranking", layout="wide")

# 1. LOAD DATA SCRAPING
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/data_univ_2000.csv')
        return df
    except:
        return None

# 2. DATA KOORDINAT NEGARA (MANUAL MAPPING)
# Ini diperlukan agar kolom 'Negara' bisa jadi titik di Peta
country_coords = {
    "USA": [37.0902, -95.7129], "China": [35.8617, 104.1954], "Japan": [36.2048, 138.2529],
    "United Kingdom": [55.3781, -3.4360], "France": [46.2276, 2.2137], "Germany": [51.1657, 10.4515],
    "Italy": [41.8719, 12.5674], "Canada": [56.1304, -106.3468], "Australia": [-25.2744, 133.7751],
    "South Korea": [35.9078, 127.7669], "Brazil": [-14.2350, -51.9253], "Spain": [40.4637, -3.7492],
    "Netherlands": [52.1326, 5.2913], "Switzerland": [46.8182, 8.2275], "Sweden": [60.1282, 18.6435],
    "Taiwan": [23.6978, 120.9605], "India": [20.5937, 78.9629], "Russia": [61.5240, 105.3188],
    "Indonesia": [-0.7893, 113.9213], "Malaysia": [4.2105, 101.9758], "Singapore": [1.3521, 103.8198],
    # Tambahkan negara lain jika perlu, atau biarkan default (0,0)
}

df = load_data()

st.title("Peta Persebaran 2.000 Universitas Terbaik Dunia")
st.markdown("Analisis data pendidikan tinggi global berdasarkan skor CWUR.")

if df is None:
    st.error("Data belum ada. Jalankan 'scrape_univ.py' terlebih dahulu!")
else:
    # --- PRE-PROCESSING GIS ---
    # Tambahkan Lat/Long ke DataFrame berdasarkan nama Negara
    lats = []
    lons = []
    
    for country in df['Negara']:
        if country in country_coords:
            # Tambahkan Random Jitter (Noise) agar titik menyebar, tidak menumpuk
            base_lat, base_lon = country_coords[country]
            lats.append(base_lat + np.random.uniform(-3.0, 3.0)) 
            lons.append(base_lon + np.random.uniform(-3.0, 3.0))
        else:
            # Default coordinate jika negara tidak ada di daftar atas (misal Eropa lain)
            lats.append(48.0 + np.random.uniform(-5.0, 5.0)) 
            lons.append(15.0 + np.random.uniform(-5.0, 5.0))

    df['lat'] = lats
    df['lon'] = lons

    # --- KPI METRICS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Universitas", f"{len(df)} Data")
    c2.metric("Negara Terdaftar", f"{df['Negara'].nunique()} Negara")
    c3.metric("Skor Tertinggi", df['Score'].max())

    st.markdown("---")

    # --- FITUR 1: GIS (PETA) ---
    st.subheader("Sebaran Universitas (Global)")
    
    fig_map = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        hover_name="Universitas",
        hover_data=["Rank", "Negara", "Score"],
        color="Negara", # Warna beda tiap negara
        zoom=1,
        height=600
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    # --- FITUR 2: VISUALISASI ---
    c_chart1, c_chart2 = st.columns(2)
    
    with c_chart1:
        st.subheader("Top 10 Negara dengan Univ Terbanyak")
        top_countries = df['Negara'].value_counts().head(10).reset_index()
        top_countries.columns = ['Negara', 'Jumlah Univ']
        
        fig_bar = px.bar(top_countries, x='Jumlah Univ', y='Negara', orientation='h', color='Jumlah Univ')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c_chart2:
        st.subheader("Distribusi Skor Kualitas")
        fig_hist = px.histogram(df, x="Score", nbins=30, title="Histogram Skor")
        st.plotly_chart(fig_hist, use_container_width=True)

    # --- FITUR 3: TABEL DATA ---
    st.markdown("---")
    st.subheader("Cari Universitas")
    search = st.text_input("Ketik nama kampus (contoh: Indonesia):")
    
    # Logika Filter
    if search:
        # Filter data berdasarkan pencarian
        df_show = df[df['Universitas'].str.contains(search, case=False) | df['Negara'].str.contains(search, case=False)]
    else:
        # Jika tidak mencari, tampilkan semua
        df_show = df
    
    # --- PERBAIKAN PENOMORAN (FIX) ---
    # 1. Reset index agar urut kembali dari 0 (jika hasil filter acak)
    df_show = df_show.reset_index(drop=True)
    
    # 2. Tambah 1 pada index agar dimulai dari angka 1, bukan 0
    df_show.index = df_show.index + 1
        
    # Tampilkan tabel
    st.dataframe(df_show, use_container_width=True)