import httpx
import pytest

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services import reply_sender


def test_send_approved_reply_success(monkeypatch):
    ticket = SimpleNamespace(
        id=1,
        chat_id=123456,
        approved_reply="Test approved reply",
        approved_reply_status="sending",
    )

    prepare_mock = MagicMock(return_value=ticket)

    send_mock = MagicMock(
        return_value={"ok": True}
    )

    finish_mock = MagicMock()

    monkeypatch.setattr(
        reply_sender, "prepare_approved_reply", prepare_mock
    )
    monkeypatch.setattr(
        reply_sender, "send_telegram_message", send_mock
    )
    monkeypatch.setattr(
        reply_sender, "finish_approved_reply", finish_mock
    )

    reply_sender.send_approved_reply(1)

    prepare_mock.assert_called_once_with(1)

    send_mock.assert_called_once_with(
        chat_id=123456,
        text="Test approved reply",
    )

    finish_mock.assert_called_once_with(
        ticket_id=1,
        delivery_status="sent",
    )

def test_send_approved_reply_failed(monkeypatch):
    ticket = SimpleNamespace(
        id=1,
        chat_id=123456,
        approved_reply="Test approved reply",
    )

    prepare_mock = MagicMock(return_value=ticket)
    send_mock = MagicMock(return_value={"ok": False})
    finish_mock = MagicMock()

    monkeypatch.setattr(
        reply_sender, "prepare_approved_reply", prepare_mock
    )
    monkeypatch.setattr(
        reply_sender, "send_telegram_message", send_mock
    )
    monkeypatch.setattr(
        reply_sender, "finish_approved_reply", finish_mock
    )

    reply_sender.send_approved_reply(1)

    finish_mock.assert_called_once_with(
        ticket_id=1,
        delivery_status="failed",
    )

def test_send_approved_reply_network_error(monkeypatch):
    ticket = SimpleNamespace(
        id=1,
        chat_id=123456,
        approved_reply="Test approved reply",
    )

    prepare_mock = MagicMock(return_value=ticket)

    send_mock = MagicMock(
        side_effect=httpx.ReadTimeout("Request timed out")
    )

    finish_mock = MagicMock()

    monkeypatch.setattr(
        reply_sender, "prepare_approved_reply", prepare_mock
    )
    monkeypatch.setattr(
        reply_sender, "send_telegram_message", send_mock
    )
    monkeypatch.setattr(
        reply_sender, "finish_approved_reply", finish_mock
    )

    reply_sender.send_approved_reply(1)

    finish_mock.assert_called_once_with(
        ticket_id=1,
        delivery_status="unknown",
    )

def test_send_approved_reply_http_400(monkeypatch):
    ticket = SimpleNamespace(
        id=1,
        chat_id=123456,
        approved_reply="Test reply",
    )

    request = httpx.Request(
        "POST", "https://api.telegram.org/sendMessage"
    )
    response = httpx.Response(400, request=request)

    error = httpx.HTTPStatusError(
        "Bad Request",
        request=request,
        response=response,
    )

    prepare_mock = MagicMock(return_value=ticket)
    send_mock = MagicMock(side_effect=error)
    finish_mock = MagicMock()

    monkeypatch.setattr(
        reply_sender, "prepare_approved_reply", prepare_mock
    )
    monkeypatch.setattr(
        reply_sender, "send_telegram_message", send_mock
    )
    monkeypatch.setattr(
        reply_sender, "finish_approved_reply", finish_mock
    )

    reply_sender.send_approved_reply(1)

    finish_mock.assert_called_once_with(
        ticket_id=1,
        delivery_status="failed",
    )

def test_send_approved_reply_http_500(monkeypatch):
    ticket = SimpleNamespace(
        id=1,
        chat_id=123456,
        approved_reply="Test reply",
    )

    request = httpx.Request(
        "POST", "https://api.telegram.org/sendMessage"
    )
    response = httpx.Response(500, request=request)

    error = httpx.HTTPStatusError(
        "Internal Server Error",
        request=request,
        response=response,
    )

    prepare_mock = MagicMock(return_value=ticket)
    send_mock = MagicMock(side_effect=error)
    finish_mock = MagicMock()

    monkeypatch.setattr(
        reply_sender, "prepare_approved_reply", prepare_mock
    )
    monkeypatch.setattr(
        reply_sender, "send_telegram_message", send_mock
    )
    monkeypatch.setattr(
        reply_sender, "finish_approved_reply", finish_mock
    )

    reply_sender.send_approved_reply(1)

    finish_mock.assert_called_once_with(
        ticket_id=1,
        delivery_status="unknown",
    )

def test_send_unapproved_reply(monkeypatch):
    prepare_mock = MagicMock(
        side_effect=ValueError("Reply is not approved")
    )
    send_mock = MagicMock()
    finish_mock = MagicMock()

    monkeypatch.setattr(
        reply_sender, "prepare_approved_reply", prepare_mock
    )
    monkeypatch.setattr(
        reply_sender, "send_telegram_message", send_mock
    )
    monkeypatch.setattr(
        reply_sender, "finish_approved_reply", finish_mock
    )

    with pytest.raises(ValueError, match="Reply is not approved"):
        reply_sender.send_approved_reply(1)

    send_mock.assert_not_called()
    finish_mock.assert_not_called()

def test_send_already_sent_reply(monkeypatch):
    prepare_mock = MagicMock(
        side_effect=ValueError("Reply is not pending delivery")
    )
    send_mock = MagicMock()
    finish_mock = MagicMock()

    monkeypatch.setattr(
        reply_sender, "prepare_approved_reply", prepare_mock
    )
    monkeypatch.setattr(
        reply_sender, "send_telegram_message", send_mock
    )
    monkeypatch.setattr(
        reply_sender, "finish_approved_reply", finish_mock
    )

    with pytest.raises(
        ValueError, match="Reply is not pending delivery"
    ):
        reply_sender.send_approved_reply(1)

    send_mock.assert_not_called()
    finish_mock.assert_not_called()

def test_send_approved_reply_http_400(monkeypatch):
    ticket = SimpleNamespace(
        id=1,
        chat_id=123456,
        approved_reply="Test reply",
    )

    request = httpx.Request(
        "POST", "https://api.telegram.org/sendMessage"
    )
    response = httpx.Response(400, request=request)

    error = httpx.HTTPStatusError(
        "Bad Request",
        request=request,
        response=response,
    )

    prepare_mock = MagicMock(return_value=ticket)
    send_mock = MagicMock(side_effect=error)
    finish_mock = MagicMock()

    monkeypatch.setattr(
        reply_sender, "prepare_approved_reply", prepare_mock
    )
    monkeypatch.setattr(
        reply_sender, "send_telegram_message", send_mock
    )
    monkeypatch.setattr(
        reply_sender, "finish_approved_reply", finish_mock
    )

    reply_sender.send_approved_reply(1)

    finish_mock.assert_called_once_with(
        ticket_id=1,
        delivery_status="failed",
    )

def test_send_approved_reply_http_500(monkeypatch):
    ticket = SimpleNamespace(
        id=1,
        chat_id=123456,
        approved_reply="Test reply",
    )

    request = httpx.Request(
        "POST", "https://api.telegram.org/sendMessage"
    )
    response = httpx.Response(500, request=request)

    error = httpx.HTTPStatusError(
        "Internal Server Error",
        request=request,
        response=response,
    )

    prepare_mock = MagicMock(return_value=ticket)
    send_mock = MagicMock(side_effect=error)
    finish_mock = MagicMock()

    monkeypatch.setattr(
        reply_sender, "prepare_approved_reply", prepare_mock
    )
    monkeypatch.setattr(
        reply_sender, "send_telegram_message", send_mock
    )
    monkeypatch.setattr(
        reply_sender, "finish_approved_reply", finish_mock
    )

    reply_sender.send_approved_reply(1)

    finish_mock.assert_called_once_with(
        ticket_id=1,
        delivery_status="unknown",
    )