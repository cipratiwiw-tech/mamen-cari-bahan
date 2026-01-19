# storage/export_csv.py

import csv
import os
from typing import List, Dict


def export_to_csv(
    records: List[Dict],
    output_dir: str,
    filename: str,
):
    """
    Export list of dict records to CSV.
    Will create directory if not exists.
    Overwrite file if already exists.
    """
    if not records:
        print("[WARN] No records to export.")
        return None

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    fieldnames = list(records[0].keys())

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter=";"
        )
        writer.writeheader()
        writer.writerows(records)


    print(f"[OK] CSV exported: {output_path}")
    return output_path


import csv
import os
from glob import glob


def load_csv_latest(platform: str, safe_keyword: str):
    data_dir = f"data/{platform}"
    files = sorted(
        glob(os.path.join(data_dir, f"*_{safe_keyword}.csv"))
    )

    if not files:
        return []

    latest = files[-1]
    rows = []

    with open(latest, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows.extend(reader)

    return rows
