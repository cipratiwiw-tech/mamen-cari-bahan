# collectors/youtube.py

from time import sleep
from urllib.parse import quote_plus
from utils.time import utc_now_iso, utc_today
from storage.visuals import prepare_screenshot_path
from utils.downloader import download_file  # <--- IMPORT BARU
import re
import random

# --- Helper Functions (Sama) ---
def parse_view_count(view_text: str | None) -> int | None:
    if not view_text: return None
    text = view_text.lower().replace("views", "").strip()
    match = re.search(r"([\d,.]+)\s*([km]?)", text)
    if not match: return None
    number, suffix = match.groups()
    number = number.replace(",", "")
    try: val = float(number)
    except ValueError: return None
    if suffix == "k": val *= 1_000
    elif suffix == "m": val *= 1_000_000
    return int(val)

def _scroll_results(page, times: int = 3):
    for _ in range(times):
        page.mouse.wheel(0, random.randint(2200, 3400))
        page.wait_for_timeout(random.randint(900, 1500))

def extract_video_id(url: str | None) -> str | None:
    if not url: return None
    if "watch?v=" in url: return url.split("watch?v=")[1].split("&")[0]
    return None
# ------------------------------

def collect_youtube_trends(page, keyword: str, max_videos: int = 30):
    results = []
    search_url = f"https://www.youtube.com/results?search_query={quote_plus(keyword)}"
    try:
        page.goto(search_url, timeout=60000)
        page.wait_for_selector("ytd-video-renderer", timeout=60000)
    except Exception as e:
        print(f"[ERROR] Gagal membuka YouTube: {e}")
        return []

    page.wait_for_timeout(random.randint(900, 1400))
    _scroll_results(page, times=3)

    video_cards = page.locator("ytd-video-renderer")
    total = video_cards.count()
    limit = min(total, max_videos)
    current_date = utc_today()

    print(f"[INFO] Collecting top {limit} videos (Real Thumbnails)...")

    for i in range(limit):
        card = video_cards.nth(i)
        try: card.scroll_into_view_if_needed(timeout=1000)
        except: pass
        page.wait_for_timeout(random.randint(200, 500))

        try:
            # 1. Ambil Info Dasar
            title_el = card.locator("#video-title").first
            title = title_el.inner_text().strip()
            href = title_el.get_attribute("href")
            video_url = f"https://www.youtube.com{href}" if href and href.startswith("/watch") else None
            video_id = extract_video_id(video_url)
            
            channel = card.locator("#channel-name a").first.inner_text().strip()
            meta = card.locator("#metadata-line span")
            raw_views = meta.nth(0).inner_text().strip() if meta.count() > 0 else None
            upload_time = meta.nth(1).inner_text().strip() if meta.count() > 1 else None
            views = parse_view_count(raw_views)

            # 2. LOGIKA DOWNLOAD THUMBNAIL ASLI
            saved_path = None
            if video_id:
                # Coba resolusi tertinggi dulu (maxres), kalau gagal fallback ke hq
                thumb_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
                
                identifier = video_id
                # Gunakan fungsi path yang sudah ada (ganti nama var jadi s_path biar konsisten)
                target_file = prepare_screenshot_path("youtube", keyword, current_date, identifier)
                
                # Lakukan Download
                success = download_file(thumb_url, target_file)
                if not success:
                    # Fallback ke HQ jika MaxRes tidak ada
                    thumb_url_hq = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                    success = download_file(thumb_url_hq, target_file)
                
                if success:
                    saved_path = target_file

            results.append({
                "platform": "youtube",
                "keyword": keyword,
                "date": current_date,
                "collected_at": utc_now_iso(),
                "title": title,
                "channel": channel,
                "views": views,
                "views_text": raw_views,
                "upload_time": upload_time,
                "url": video_url,
                "video_id": video_id,
                "screenshot": saved_path, # GUI membaca key 'screenshot'
            })

        except Exception as e:
            print(f"[WARN] Skip index {i}: {e}")
            continue

    return results