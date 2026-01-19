# runner.py

import os
import sys

from browser.launcher import launch_browser
from collectors.youtube import collect_youtube_trends
from collectors.tiktok import collect_tiktok_trends
from storage.export_csv import export_to_csv
from utils.time import utc_today

from analysis.trend_delta import compare_daily_csv, export_trend_delta
from analysis.export_early_breakout import export_early_breakout_only

from enrich.youtube_api_enricher import enrich_youtube_records


DATA_DIR_YT = "data/youtube"
DATA_DIR_TT = "data/tiktok"


def run_collect(platform: str, keyword: str) -> str:
    p, browser, page = launch_browser(headless=True)
    safe_keyword = keyword.replace(" ", "-")
    date = utc_today()

    try:
        if platform == "youtube":
            data = collect_youtube_trends(page, keyword, max_videos=20)
            data = enrich_youtube_records(data)

            out_dir = DATA_DIR_YT
        elif platform == "tiktok":
            data = collect_tiktok_trends(page, keyword, max_videos=20)
            out_dir = DATA_DIR_TT
        else:
            raise ValueError("platform must be youtube or tiktok")
    except Exception as e:
        print(f"[ERROR] Collect failed: {e}")
        browser.close()
        p.stop()
        return safe_keyword

    if not data:
        print("[WARN] No data collected, skip export.")
        browser.close()
        p.stop()
        return safe_keyword

    export_to_csv(
        records=data,
        output_dir=out_dir,
        filename=f"{date}_{safe_keyword}.csv",
    )

    browser.close()
    p.stop()

    return safe_keyword


def run_compare(platform: str, safe_keyword: str):
    data_dir = DATA_DIR_YT if platform == "youtube" else DATA_DIR_TT

    if not os.path.exists(data_dir):
        return

    files = sorted(
        f for f in os.listdir(data_dir)
        if f.endswith(f"_{safe_keyword}.csv")
        and not f.startswith("trend_")
        and not f.startswith("early_breakout_")
    )

    if len(files) < 2:
        print("[INFO] Not enough history to compare.")
        return

    yesterday = os.path.join(data_dir, files[-2])
    today = os.path.join(data_dir, files[-1])

    delta_records = compare_daily_csv(today, yesterday)

    trend_path = os.path.join(data_dir, f"trend_{files[-1]}")
    export_trend_delta(delta_records, trend_path)

    early_path = os.path.join(data_dir, f"early_breakout_{files[-1]}")
    export_early_breakout_only(delta_records, early_path)


def main():
    if len(sys.argv) < 3:
        print('Usage: python runner.py <youtube|tiktok> "keyword"')
        sys.exit(1)

    platform = sys.argv[1].lower()
    keyword = sys.argv[2]

    if platform not in ("youtube", "tiktok"):
        print("Platform must be: youtube or tiktok")
        sys.exit(1)

    safe_keyword = run_collect(platform, keyword)
    run_compare(platform, safe_keyword)


if __name__ == "__main__":
    main()
