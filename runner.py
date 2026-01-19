from browser.launcher import launch_browser
from collectors.youtube import collect_youtube_trends
from storage.export_csv import export_to_csv
from utils.time import utc_today
from analysis.trend_delta import compare_daily_csv, export_trend_delta
import os


def run_collect():
    p, browser, page = launch_browser()

    keyword = "ai tools"
    data = collect_youtube_trends(page, keyword, max_videos=20)

    date = utc_today()
    safe_keyword = keyword.replace(" ", "-")
    out_dir = "data/youtube"

    today_csv = export_to_csv(
        records=data,
        output_dir=out_dir,
        filename=f"{date}_{safe_keyword}.csv",
    )

    browser.close()
    p.stop()

    return today_csv, safe_keyword


def run_compare(today_csv: str, safe_keyword: str):
    # tentukan file kemarin
    files = sorted(
        f for f in os.listdir("data/youtube")
        if f.endswith(f"_{safe_keyword}.csv")
    )

    if len(files) < 2:
        print("[INFO] Not enough history to compare.")
        return

    yesterday_csv = os.path.join("data/youtube", files[-2])
    today_csv = os.path.join("data/youtube", files[-1])

    delta_records = compare_daily_csv(today_csv, yesterday_csv)

    export_trend_delta(
        delta_records,
        output_path=f"data/youtube/trend_{files[-1]}",
    )


def main():
    today_csv, safe_keyword = run_collect()
    run_compare(today_csv, safe_keyword)


if __name__ == "__main__":
    main()
