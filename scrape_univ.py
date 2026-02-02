import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def scrape_univ_world():
    # URL Scraping
    url = "https://cwur.org/2023.php"
    
    print("=== SCRAPING 2000 UNIVERSITAS TERBAIK DUNIA ===")
    print(f"Target URL: {url}")
    
    # Headers browser 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Cari tabel (biasanya id='cwurTable')
        table = soup.find('table', id='cwurTable')
        
        if not table:
            # Fallback jika ID berubah, cari tag table biasa
            table = soup.find('table')

        if not table:
            print("Gagal menemukan tabel data.")
            return

        all_univ = []
        # Ambil semua baris (tr) di dalam tbody
        rows = table.find('tbody').find_all('tr')
        
        print(f"Menemukan {len(rows)} baris data...")

        for row in rows:
            cols = row.find_all('td')
            # Struktur kolom biasanya: [Rank, Institution, Location, Quality..., Score]
            if len(cols) >= 4:
                rank = cols[0].text.strip()
                nama_univ = cols[1].text.strip()
                negara = cols[2].text.strip()
                score = cols[-1].text.strip() # Score biasanya di kolom terakhir
                
                all_univ.append({
                    "Rank": rank,
                    "Universitas": nama_univ,
                    "Negara": negara,
                    "Score": score
                })

        # SIMPAN KE CSV
        if all_univ:
            if not os.path.exists('data'):
                os.makedirs('data')
                
            df = pd.DataFrame(all_univ)
            filename = 'data/data_univ_2000.csv'
            df.to_csv(filename, index=False)
            
            print("\n" + "="*50)
            print(f"✅ SUKSES! Berhasil mengambil {len(df)} data.")
            print(f"File tersimpan: {filename}")
            print("="*50)
            print(df.head())
        else:
            print("Data kosong setelah parsing.")

    except Exception as e:
        print(f"Terjadi error: {e}")

if __name__ == "__main__":
    scrape_univ_world()