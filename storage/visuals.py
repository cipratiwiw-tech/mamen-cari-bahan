# storage/visuals.py

import os
import re

def prepare_screenshot_path(platform: str, keyword: str, date: str, identifier: str) -> str:
    """
    Menyiapkan path lengkap untuk menyimpan screenshot.
    Struktur folder: storage/screenshots/{date}/{platform}/{keyword}/filename.jpg
    """
    base_dir = "storage/screenshots"
    
    # 1. Bersihkan keyword dan identifier dari karakter ilegal file system
    safe_keyword = re.sub(r'[\\/*?:"<>|]', "", keyword).replace(" ", "-")
    
    # Bersihkan identifier (judul/ID), ganti spasi dengan underscore, limit panjang 60 karakter
    safe_id = re.sub(r'[\\/*?:"<>|]', "", identifier).replace(" ", "_")
    safe_id = safe_id[:60] 
    
    # 2. Buat struktur folder jika belum ada
    full_dir = os.path.join(base_dir, date, platform, safe_keyword)
    os.makedirs(full_dir, exist_ok=True)
    
    # 3. Return full path
    return os.path.join(full_dir, f"{safe_id}.jpg")