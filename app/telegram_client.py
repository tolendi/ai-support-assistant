import os

import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")


TELEGRAM_API_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
)


def get_bot_info():
    response = httpx.get(
        f"{TELEGRAM_API_URL}/getMe",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def parse_telegram_message(update: dict):
    message = update.get("message")

    if not message:
        return None

    text = message.get("text")

    if not text:
        return None

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]

    return {
        "chat_id": chat_id,
        "user_id": user_id,
        "message_id": message_id,
        "text": text,
    }


def send_telegram_message(chat_id: int, text: str):
    try:
        response = httpx.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except httpx.RequestError as error:
        print(f"Telegram connection error: {error}")
        raise

    except httpx.HTTPStatusError as error:
        print(f"Telegram API error: {error}")
        raise