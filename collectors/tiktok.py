# collectors/tiktok.py

from urllib.parse import quote_plus
from utils.time import utc_today, utc_now_iso
import random
import re


def _parse_views(text: str | None) -> int | None:
    if not text:
        return None

    text = text.lower().strip()
    m = re.search(r"([\d,.]+)\s*([km]?)", text)
    if not m:
        return None

    num, suf = m.groups()
    num = num.replace(",", "")
    try:
        val = float(num)
    except ValueError:
        return None

    if suf == "k":
        val *= 1_000
    elif suf == "m":
        val *= 1_000_000

    return int(val)


def _human_wait(page, a=800, b=1500):
    page.wait_for_timeout(random.randint(a, b))


def _scroll(page, times=4):
    for _ in range(times):
        page.mouse.wheel(0, random.randint(2500, 4000))
        _human_wait(page, 900, 1600)


def collect_tiktok_trends(page, keyword: str, max_videos: int = 20):
    results = []

    search_url = f"https://www.tiktok.com/search?q={quote_plus(keyword)}"
    page.goto(search_url, timeout=60000)

    # 🔴 JANGAN tunggu selector spesifik dulu
    _human_wait(page, 1500, 2500)

    # 🔴 Scroll dulu biar React render
    _scroll(page, times=2)

    # 🔴 Selector fallback (INI KUNCI)
    selectors = [
        "div[data-e2e='search-video-item']",
        "div[data-e2e='search_top-item']",
        "div.tiktok-yz6ijl-DivWrapper",
    ]

    cards = None
    for sel in selectors:
        if page.locator(sel).count() > 0:
            cards = page.locator(sel)
            break

    if not cards or cards.count() == 0:
        raise RuntimeError("TikTok search results not found (DOM changed or blocked)")

    total = cards.count()
    limit = min(total, max_videos)

    for i in range(limit):
        card = cards.nth(i)
        _human_wait(page, 300, 700)

        try:
            # URL
            href = (
                card.locator("a[href*='/video/']").first.get_attribute("href")
                if card.locator("a[href*='/video/']").count() > 0
                else None
            )
            video_url = href if href and href.startswith("http") else None

            # Caption / title (TikTok sering kosong)
            title = ""
            if card.locator("a[href*='/video/']").count() > 0:
                title = card.locator("a[href*='/video/']").first.inner_text().strip()

            # Author
            channel = ""
            if card.locator("a[href^='/@']").count() > 0:
                channel = card.locator("a[href^='/@']").first.inner_text().strip()

            # Views (paling tidak stabil)
            views_text = None
            if card.locator("strong").count() > 0:
                views_text = card.locator("strong").first.inner_text().strip()

            views = _parse_views(views_text)

            results.append(
                {
                    "platform": "tiktok",
                    "keyword": keyword,
                    "date": utc_today(),
                    "collected_at": utc_now_iso(),
                    "title": title,
                    "channel": channel,
                    "views": views,
                    "views_text": views_text,
                    "upload_time": None,
                    "url": video_url,
                }
            )

        except Exception as e:
            print(f"[WARN] TikTok skip index {i}: {e}")
            continue

    return results
