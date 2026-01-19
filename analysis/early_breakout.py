# analysis/early_breakout.py

from typing import Dict, List


def is_early_breakout(record: Dict) -> bool:
    age = record.get("age_days_est")
    delta = record.get("delta_views")
    views = record.get("views_today") or record.get("views")
    score = record.get("trend_score")

    if age is None or delta is None or views is None or score is None:
        return False

    if age > 7:
        return False

    if delta < 2000:
        return False

    if views > 500_000:
        return False

    if score < 40:
        return False

    return True


def mark_early_breakouts(records: List[Dict]) -> List[Dict]:
    for r in records:
        r["early_breakout"] = is_early_breakout(r)
    return records


def filter_early_breakouts(records: List[Dict]) -> List[Dict]:
    return [r for r in records if r.get("early_breakout")]
