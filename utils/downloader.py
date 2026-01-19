# utils/downloader.py

import requests
import os

def download_file(url: str, save_path: str):
    """
    Download file dari URL dan simpan ke path lokal.
    Mengembalikan True jika sukses.
    """
    if not url:
        return False
        
    try:
        # Timeout 10 detik agar tidak hang
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"[ERROR] Gagal download {url}: {e}")
    
    return False