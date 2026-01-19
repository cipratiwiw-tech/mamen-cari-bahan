# collectors/tiktok.py

from urllib.parse import quote_plus
from utils.time import utc_today, utc_now_iso
from storage.visuals import prepare_screenshot_path
from utils.downloader import download_file # <--- IMPORT BARU
import random
import re

# --- Helper Functions (Sama) ---
def _parse_views(text: str | None) -> int | None:
    if not text: return None
    text = text.lower().strip()
    m = re.search(r"([\d,.]+)\s*([km]?)", text)
    if not m: return None
    num, suf = m.groups()
    num = num.replace(",", "")
    try: val = float(num)
    except ValueError: return None
    if suffix == "k": val *= 1_000
    elif suffix == "m": val *= 1_000_000
    return int(val)

def _human_wait(page, a=800, b=1500):
    page.wait_for_timeout(random.randint(a, b))

def _scroll(page, times=4):
    for _ in range(times):
        page.mouse.wheel(0, random.randint(2500, 4000))
        _human_wait(page, 900, 1600)
# ------------------------------

def collect_tiktok_trends(page, keyword: str, max_videos: int = 20):
    results = []
    search_url = f"https://www.tiktok.com/search?q={quote_plus(keyword)}"
    try:
        page.goto(search_url, timeout=60000)
    except Exception as e:
        print(f"[ERROR] Gagal membuka TikTok: {e}")
        return []

    _human_wait(page, 1500, 2500)
    _scroll(page, times=2)

    selectors = ["div[data-e2e='search-video-item']", "div[data-e2e='search_top-item']"]
    cards = None
    for sel in selectors:
        if page.locator(sel).count() > 0:
            cards = page.locator(sel)
            break
            
    if not cards or cards.count() == 0:
        print("[WARN] TikTok selectors not found.")
        return []

    total = cards.count()
    limit = min(total, max_videos)
    current_date = utc_today()
    print(f"[INFO] Collecting {limit} TikToks (Real Covers)...")

    for i in range(limit):
        card = cards.nth(i)
        try: card.scroll_into_view_if_needed(timeout=1000)
        except: pass
        _human_wait(page, 300, 700)

        try:
            # 1. Info Dasar
            href = None
            link_el = card.locator("a[href*='/video/']")
            if link_el.count() > 0: href = link_el.first.get_attribute("href")
            video_url = href if href and href.startswith("http") else None
            
            title = link_el.first.inner_text().strip() if link_el.count() > 0 else ""
            
            channel = ""
            author_el = card.locator("a[href^='/@']")
            if author_el.count() > 0: channel = author_el.first.inner_text().strip()
            
            views_text = None
            if card.locator("strong").count() > 0:
                views_text = card.locator("strong").first.inner_text().strip()
            views = _parse_views(views_text)

            # 2. LOGIKA DOWNLOAD COVER ASLI
            saved_path = None
            try:
                # Cari tag IMG di dalam link video
                # Biasanya TikTok menaruh cover image di dalam link tersebut
                img_el = link_el.locator("img").first
                img_src = img_el.get_attribute("src") if img_el.count() > 0 else None
                
                if img_src:
                    # Bersihkan nama file
                    safe_title = title if title else f"tiktok_{i}_{random.randint(100,999)}"
                    target_file = prepare_screenshot_path("tiktok", keyword, current_date, safe_title)
                    
                    success = download_file(img_src, target_file)
                    if success:
                        saved_path = target_file
            except Exception as e:
                print(f"[WARN] Gagal ambil cover tiktok {i}: {e}")

            results.append({
                "platform": "tiktok",
                "keyword": keyword,
                "date": current_date,
                "collected_at": utc_now_iso(),
                "title": title,
                "channel": channel,
                "views": views,
                "views_text": views_text,
                "upload_time": None,
                "url": video_url,
                "screenshot": saved_path, # Key tetap 'screenshot' agar kompatibel
            })

        except Exception as e:
            print(f"[WARN] TikTok skip index {i}: {e}")
            continue

    return results