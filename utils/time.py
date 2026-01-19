# utils/time.py

from datetime import datetime, timezone


def utc_now_iso() -> str:
    """
    Return current UTC time in ISO 8601 format.
    Example: 2026-01-19T05:12:33Z
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_today() -> str:
    """
    Return current UTC date.
    Example: 2026-01-19
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
