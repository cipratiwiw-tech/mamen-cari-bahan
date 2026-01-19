# bot_listener.py

import time
import requests
import yaml

from browser.launcher import launch_browser
from collectors.youtube import collect_youtube_trends
from analysis.trend_delta import compare_daily_csv
from analysis.export_early_breakout import export_early_breakout_only
from notifications.formatters import format_early_breakout
from utils.time import utc_today
from storage.export_csv import export_to_csv

DATA_DIR = "data/youtube"


def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_updates(bot_token, offset=None):
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    return requests.get(url, params=params, timeout=40).json()


def send_message(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=10,
    )


def handle_keyword(keyword: str):
    p, browser, page = launch_browser()

    data = collect_youtube_trends(page, keyword, max_videos=20)

    date = utc_today()
    safe_keyword = keyword.replace(" ", "-")

    today_csv = export_to_csv(
        records=data,
        output_dir=DATA_DIR,
        filename=f"{date}_{safe_keyword}.csv",
    )

    browser.close()
    p.stop()

    # cari file sebelumnya
    files = sorted(
        f for f in os.listdir(DATA_DIR)
        if f.endswith(f"_{safe_keyword}.csv")
        and not f.startswith("trend_")
        and not f.startswith("early_breakout_")
    )

    if len(files) < 2:
        return [], safe_keyword, date

    yesterday = f"{DATA_DIR}/{files[-2]}"
    today = f"{DATA_DIR}/{files[-1]}"

    delta_records = compare_daily_csv(today, yesterday)

    return delta_records, safe_keyword, date


def main():
    cfg = load_config()
    tg = cfg["telegram"]

    bot_token = tg["bot_token"]
    chat_id = tg["chat_id"]

    offset = None

    print("🤖 Bot listener running...")

    while True:
        updates = get_updates(bot_token, offset)

        if not updates.get("ok"):
            time.sleep(5)
            continue

        for update in updates["result"]:
            offset = update["update_id"] + 1

            message = update.get("message")
            if not message:
                continue

            text = message.get("text", "").strip()
            if not text:
                continue

            keyword = text.lower()

            send_message(bot_token, chat_id, f"🔍 Researching: <b>{keyword}</b>")

            records, safe_keyword, date = handle_keyword(keyword)

            breakout_only = [r for r in records if r.get("early_breakout")]

            reply = format_early_breakout(
                breakout_only,
                keyword=keyword,
                date=date,
            )

            send_message(bot_token, chat_id, reply)

        time.sleep(1)


if __name__ == "__main__":
    main()
