# runner.py

import os

from browser.launcher import launch_browser
from collectors.youtube import collect_youtube_trends
from storage.export_csv import export_to_csv
from utils.time import utc_today

from analysis.trend_delta import compare_daily_csv, export_trend_delta
from analysis.export_early_breakout import export_early_breakout_only


DATA_DIR = "data/youtube"


def run_collect(keyword: str) -> str:
    p, browser, page = launch_browser(headless=True)

    data = collect_youtube_trends(page, keyword, max_videos=20)

    date = utc_today()
    safe_keyword = keyword.replace(" ", "-")

    export_to_csv(
        records=data,
        output_dir=DATA_DIR,
        filename=f"{date}_{safe_keyword}.csv",
    )

    browser.close()
    p.stop()

    return safe_keyword


def run_compare(safe_keyword: str):
    files = sorted(
        f for f in os.listdir(DATA_DIR)
        if f.endswith(f"_{safe_keyword}.csv")
        and not f.startswith("trend_")
        and not f.startswith("early_breakout_")
    )

    if len(files) < 2:
        print("[INFO] Not enough history to compare.")
        return

    yesterday = os.path.join(DATA_DIR, files[-2])
    today = os.path.join(DATA_DIR, files[-1])

    delta_records = compare_daily_csv(today, yesterday)

    trend_path = os.path.join(DATA_DIR, f"trend_{files[-1]}")
    export_trend_delta(delta_records, trend_path)

    early_path = os.path.join(DATA_DIR, f"early_breakout_{files[-1]}")
    export_early_breakout_only(delta_records, early_path)


def main():
    keyword = "ai tools"

    safe_keyword = run_collect(keyword)
    run_compare(safe_keyword)


if __name__ == "__main__":
    main()
