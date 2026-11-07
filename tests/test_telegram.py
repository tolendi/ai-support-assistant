import httpx
import pytest

from app import telegram_client
from app.telegram_client import parse_telegram_message


def test_parse_telegram_message():
    update = {
        "message": {
            "message_id": 101,
            "from": {"id": 555},
            "chat": {"id": 555},
            "text": "I was charged twice",
        }
    }

    result = parse_telegram_message(update)

    assert result == {
        "chat_id": 555,
        "user_id": 555,
        "message_id": 101,
        "text": "I was charged twice",
    }


def test_parse_telegram_message_without_message():
    update = {"update_id": 123}

    result = parse_telegram_message(update)

    assert result is None


def test_parse_telegram_message_without_text():
    update = {
        "message": {
            "message_id": 102,
            "from": {"id": 555},
            "chat": {"id": 555},
            "photo": [],
        }
    }

    result = parse_telegram_message(update)

    assert result is None


def test_send_telegram_message_connection_error(monkeypatch):
    def mock_post(*args, **kwargs):
        raise httpx.RequestError("Connection failed")

    monkeypatch.setattr(telegram_client.httpx, "post", mock_post)

    with pytest.raises(httpx.RequestError):
        telegram_client.send_telegram_message(
            chat_id=555,
            text="Test message",
        )


def test_send_telegram_message_http_error(monkeypatch):
    def mock_post(*args, **kwargs):
        request = httpx.Request("POST", "https://api.telegram.org/bot123/sendMessage")
        response = httpx.Response(400, request=request)
        return response

    monkeypatch.setattr(telegram_client.httpx, "post", mock_post)

    with pytest.raises(httpx.HTTPStatusError):
        telegram_client.send_telegram_message(
            chat_id=555,
            text="Test message",
        )