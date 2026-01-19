# analysis/trend_delta.py

import csv
import os
from typing import Dict, List
from datetime import datetime


def _read_csv(path: str) -> List[Dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)
    return rows


def _index_by_url(rows: List[Dict]) -> Dict[str, Dict]:
    return {row["url"]: row for row in rows if row.get("url")}


def compare_daily_csv(today_csv: str, yesterday_csv: str) -> List[Dict]:
    """
    Compare two CSV files (today vs yesterday) and compute delta & velocity.
    """
    today_rows = _read_csv(today_csv)
    yesterday_rows = _read_csv(yesterday_csv)

    today_by_url = _index_by_url(today_rows)
    yest_by_url = _index_by_url(yesterday_rows)

    results = []

    for url, today in today_by_url.items():
        if url not in yest_by_url:
            # Video baru (belum ada kemarin)
            results.append({
                **today,
                "views_yesterday": None,
                "views_today": int(today["views"]) if today.get("views") else None,
                "delta_views": None,
                "velocity_per_day": None,
                "status": "new",
            })
            continue

        yest = yest_by_url[url]

        try:
            vt = int(today["views"])
            vy = int(yest["views"])
            delta = vt - vy
        except (TypeError, ValueError):
            vt, vy, delta = None, None, None

        results.append({
            **today,
            "views_yesterday": vy,
            "views_today": vt,
            "delta_views": delta,
            "velocity_per_day": delta,  # 1-day diff
            "status": "existing",
        })

    return results


def export_trend_delta(records: List[Dict], output_path: str):
    if not records:
        print("[WARN] No trend delta records.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fieldnames = list(records[0].keys())

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(records)

    print(f"[OK] Trend delta exported: {output_path}")
