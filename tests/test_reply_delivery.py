from unittest.mock import MagicMock

import pytest

from app import database
from app.models import Ticket


def test_prepare_approved_reply_success(monkeypatch):
    ticket = Ticket(
        id=1,
        chat_id=123456,
        review_status="approved",
        approved_reply="Test approved reply",
        approved_reply_status="pending",
    )

    session = MagicMock()
    session.get.return_value = ticket
    session.__enter__.return_value = session

    monkeypatch.setattr(
        database, "SessionLocal", lambda: session
    )

    result = database.prepare_approved_reply(1)

    assert result.approved_reply_status == "sending"

    session.get.assert_called_once_with(
        Ticket, 1, with_for_update=True
    )

    session.commit.assert_called_once()

def test_prepare_nonexistent_ticket(monkeypatch):
    session = MagicMock()
    session.get.return_value = None
    session.__enter__.return_value = session

    monkeypatch.setattr(
        database, "SessionLocal", lambda: session
    )

    result = database.prepare_approved_reply(1)

    assert result is None
    session.commit.assert_not_called()

def test_prepare_unapproved_reply(monkeypatch):
    ticket = Ticket(
        id=1,
        review_status="pending_review",
    )

    session = MagicMock()
    session.get.return_value = ticket
    session.__enter__.return_value = session

    monkeypatch.setattr(
        database, "SessionLocal", lambda: session
    )

    with pytest.raises(ValueError, match="Reply is not approved"):
        database.prepare_approved_reply(1)

    session.commit.assert_not_called()

def test_prepare_reply_without_chat_id(monkeypatch):
    ticket = Ticket(
        id=1,
        review_status="approved",
        chat_id=None,
    )

    session = MagicMock()
    session.get.return_value = ticket
    session.__enter__.return_value = session

    monkeypatch.setattr(
        database, "SessionLocal", lambda: session
    )

    with pytest.raises(ValueError, match="Ticket has no chat_id"):
        database.prepare_approved_reply(1)

    session.commit.assert_not_called()

def test_prepare_empty_approved_reply(monkeypatch):
    ticket = Ticket(
        id=1,
        review_status="approved",
        chat_id=123456,
        approved_reply="   ",
        approved_reply_status="pending",
    )

    session = MagicMock()
    session.get.return_value = ticket
    session.__enter__.return_value = session

    monkeypatch.setattr(
        database, "SessionLocal", lambda: session
    )

    with pytest.raises(ValueError, match="Approved reply is empty"):
        database.prepare_approved_reply(1)

    session.commit.assert_not_called()

@pytest.mark.parametrize(
    "delivery_status",
    ["sending", "sent", "failed", "unknown"],
)
def test_prepare_reply_invalid_delivery_status(
    monkeypatch, delivery_status
):
    ticket = Ticket(
        id=1,
        review_status="approved",
        chat_id=123456,
        approved_reply="Test approved reply",
        approved_reply_status=delivery_status,
    )

    session = MagicMock()
    session.get.return_value = ticket
    session.__enter__.return_value = session

    monkeypatch.setattr(
        database, "SessionLocal", lambda: session
    )

    with pytest.raises(
        ValueError, match="Reply is not pending delivery"
    ):
        database.prepare_approved_reply(1)

    assert ticket.approved_reply_status == delivery_status
    session.commit.assert_not_called()

def test_finish_approved_reply_sent(monkeypatch):
    ticket = Ticket(
        id=1,
        approved_reply_status="sending",
    )

    session = MagicMock()
    session.get.return_value = ticket
    session.__enter__.return_value = session

    monkeypatch.setattr(
        database, "SessionLocal", lambda: session
    )

    result = database.finish_approved_reply(1, "sent")

    assert result.approved_reply_status == "sent"
    assert result.approved_reply_sent_at is not None

    session.commit.assert_called_once()

@pytest.mark.parametrize(
    "delivery_status",
    ["failed", "unknown"],
)
def test_finish_approved_reply_unsuccessful(
    monkeypatch, delivery_status
):
    ticket = Ticket(
        id=1,
        approved_reply_status="sending",
        approved_reply_sent_at=None,
    )

    session = MagicMock()
    session.get.return_value = ticket
    session.__enter__.return_value = session

    monkeypatch.setattr(
        database, "SessionLocal", lambda: session
    )

    result = database.finish_approved_reply(
        1, delivery_status
    )

    assert result.approved_reply_status == delivery_status
    assert result.approved_reply_sent_at is None

    session.commit.assert_called_once()

def test_finish_invalid_delivery_status(monkeypatch):
    session_mock = MagicMock()

    monkeypatch.setattr(
        database, "SessionLocal", session_mock
    )

    with pytest.raises(
        ValueError, match="Invalid delivery status"
    ):
        database.finish_approved_reply(1, "invalid")

    session_mock.assert_not_called()

def test_finish_nonexistent_ticket(monkeypatch):
    session = MagicMock()
    session.get.return_value = None
    session.__enter__.return_value = session

    monkeypatch.setattr(
        database, "SessionLocal", lambda: session
    )

    result = database.finish_approved_reply(1, "sent")

    assert result is None
    session.commit.assert_not_called()

@pytest.mark.parametrize(
    "current_status",
    ["pending", "sent", "failed", "unknown"],
)
def test_finish_reply_invalid_transition(
    monkeypatch, current_status
):
    ticket = Ticket(
        id=1,
        approved_reply_status=current_status,
    )

    session = MagicMock()
    session.get.return_value = ticket
    session.__enter__.return_value = session

    monkeypatch.setattr(
        database, "SessionLocal", lambda: session
    )

    with pytest.raises(
        ValueError, match="Reply is not being sent"
    ):
        database.finish_approved_reply(1, "sent")

    assert ticket.approved_reply_status == current_status
    session.commit.assert_not_called()