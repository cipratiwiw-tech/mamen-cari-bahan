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
