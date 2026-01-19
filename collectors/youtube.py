# collectors/youtube.py

from time import sleep
from urllib.parse import quote_plus
from utils.time import utc_now_iso, utc_today

import re
import random


def parse_view_count(view_text: str | None) -> int | None:
    if not view_text:
        return None

    text = view_text.lower().replace("views", "").strip()
    match = re.search(r"([\d,.]+)\s*([km]?)", text)

    if not match:
        return None

    number, suffix = match.groups()
    number = number.replace(",", "")

    try:
        value = float(number)
    except ValueError:
        return None

    if suffix == "k":
        value *= 1_000
    elif suffix == "m":
        value *= 1_000_000

    return int(value)


def _scroll_results(page, times: int = 3):
    for _ in range(times):
        page.mouse.wheel(0, random.randint(2200, 3400))
        page.wait_for_timeout(random.randint(900, 1500))



def collect_youtube_trends(page, keyword: str, max_videos: int = 30):
    results = []

    search_url = f"https://www.youtube.com/results?search_query={quote_plus(keyword)}"
    page.goto(search_url, timeout=60000)
    page.wait_for_selector("ytd-video-renderer", timeout=60000)
    page.wait_for_timeout(random.randint(900, 1400))




    _scroll_results(page, times=3)

    video_cards = page.locator("ytd-video-renderer")
    total = video_cards.count()
    limit = min(total, max_videos)

    for i in range(limit):
        card = video_cards.nth(i)
        page.wait_for_timeout(random.randint(300, 650))


        try:
            title_el = card.locator("#video-title").first
            title = title_el.inner_text().strip()
            href = title_el.get_attribute("href")

            video_url = (
                f"https://www.youtube.com{href}"
                if href and href.startswith("/watch")
                else None
            )

            channel = card.locator("#channel-name a").first.inner_text().strip()

            meta = card.locator("#metadata-line span")
            raw_views = meta.nth(0).inner_text().strip() if meta.count() > 0 else None
            upload_time = meta.nth(1).inner_text().strip() if meta.count() > 1 else None

            views = parse_view_count(raw_views)

            results.append({
                "platform": "youtube",
                "keyword": keyword,

                # --- TIME SNAPSHOT ---
                "date": utc_today(),
                "collected_at": utc_now_iso(),

                # --- CONTENT ---
                "title": title,
                "channel": channel,
                "views": views,
                "views_text": raw_views,
                "upload_time": upload_time,
                "url": video_url,
            })


        except Exception as e:
            print(f"[WARN] Skip index {i}: {e}")
            continue

    return results
