# notifications/formatters.py

def format_early_breakout(records: list, keyword: str, date: str) -> str:
    """
    Format early breakout records into a Telegram-friendly message.
    """

    if not records:
        return (
            f"📉 <b>No early breakout</b>\n"
            f"Keyword: <b>{keyword}</b>\n"
            f"Date: {date}"
        )

    lines = [
        "🚀 <b>EARLY BREAKOUT DETECTED</b>",
        f"Keyword: <b>{keyword}</b>",
        f"Date: {date}",
        "",
    ]

    for i, r in enumerate(records[:3], start=1):
        lines.append(
            f"{i}. <b>{r.get('title')}</b>\n"
            f"   Channel: {r.get('channel')}\n"
            f"   Views: {r.get('views_today')} (+{r.get('delta_views')})\n"
            f"   Score: {r.get('trend_score')} ({r.get('trend_label')})\n"
            f"   🔗 {r.get('url')}\n"
        )

    return "\n".join(lines)
