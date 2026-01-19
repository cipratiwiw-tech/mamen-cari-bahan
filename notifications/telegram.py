# notifications/telegram.py

import requests


def send_telegram_message(bot_token: str, chat_id: str, text: str):
    """
    Send a text message to Telegram using Bot API.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
