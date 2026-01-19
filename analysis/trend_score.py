# analysis/trend_score.py

from typing import Dict, List
import re


def _estimate_age_days(upload_time: str | None) -> int | None:
    """
    Convert '2 days ago', '3 months ago', etc. to rough days.
    """
    if not upload_time:
        return None

    text = upload_time.lower()
    match = re.search(r"(\d+)\s+(hour|day|week|month|year)", text)
    if not match:
        return None

    value = int(match.group(1))
    unit = match.group(2)

    if unit == "hour":
        return max(1, value // 24)
    if unit == "day":
        return value
    if unit == "week":
        return value * 7
    if unit == "month":
        return value * 30
    if unit == "year":
        return value * 365

    return None


def compute_trend_score(record: Dict) -> Dict:
    """
    Compute trend score and label for a video record.
    """
    views = record.get("views_api") or record.get("views")

    delta = record.get("delta_views")
    age_days = _estimate_age_days(record.get("upload_time"))

    score = 0.0

    # 1. Momentum (most important)
    if delta and delta > 0:
        score += min(delta / 1000, 50)  # cap momentum

    # 2. Scale (log-ish)
    if views:
        score += min(views / 100000, 30)

    # 3. Freshness boost
    if age_days is not None:
        if age_days <= 2:
            score += 30
        elif age_days <= 7:
            score += 20
        elif age_days <= 30:
            score += 10

    # Labeling
    if score >= 70:
        label = "爆发"      # breakout
    elif score >= 40:
        label = "rising"
    elif score >= 20:
        label = "stable"
    else:
        label = "stale"

    record["trend_score"] = round(score, 2)
    record["trend_label"] = label
    record["age_days_est"] = age_days

    return record


def score_records(records: List[Dict]) -> List[Dict]:
    scored = [compute_trend_score(r) for r in records]
    return sorted(scored, key=lambda x: x.get("trend_score", 0), reverse=True)
