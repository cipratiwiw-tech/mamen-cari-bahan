# analysis/export_early_breakout.py

import csv
import os
from typing import List, Dict


def export_early_breakout_only(
    records: List[Dict],
    output_path: str,
):
    """
    Export only early breakout records to CSV.
    If no breakout found, still create CSV with header.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    breakout_records = [r for r in records if r.get("early_breakout")]

    # Tentukan fieldnames (ambil dari records pertama jika ada)
    if records:
        fieldnames = list(records[0].keys())
    else:
        fieldnames = []

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        if breakout_records:
            writer.writerows(breakout_records)

    print(
        f"[OK] Early breakout CSV exported: {output_path} "
        f"(count={len(breakout_records)})"
    )
