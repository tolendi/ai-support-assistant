from unittest.mock import MagicMock

from app import database
from app.models import Ticket
import pytest


def test_approve_ticket_reply(monkeypatch):
    ticket = Ticket(
        id=1,
        review_status="pending_review",
    )

    session = MagicMock()
    session.get.return_value = ticket

    monkeypatch.setattr(
        database,
        "SessionLocal",
        lambda: session,
    )

    session.__enter__.return_value = session

    result = database.approve_ticket_reply(
        ticket_id=1,
        operator_id=100,
        approved_reply="Test approved reply",
    )

    assert result.review_status == "approved"
    assert result.approved_reply == "Test approved reply"
    assert result.reviewed_by == 100
    assert result.reviewed_at is not None

    session.commit.assert_called_once()

def test_approve_already_approved_ticket(monkeypatch):
    ticket = Ticket(
        id=1,
        review_status="approved",
    )

    session = MagicMock()
    session.get.return_value = ticket
    session.__enter__.return_value = session

    monkeypatch.setattr(database, "SessionLocal", lambda: session)

    with pytest.raises(ValueError, match="Ticket is not pending review"):
        database.approve_ticket_reply(1, 100, "Another reply")

    session.commit.assert_not_called()

def test_approve_nonexistent_ticket(monkeypatch):
    session = MagicMock()
    session.get.return_value = None
    session.__enter__.return_value = session

    monkeypatch.setattr(database, "SessionLocal", lambda: session)

    result = database.approve_ticket_reply(1, 100, "Test reply")

    assert result is None
    session.commit.assert_not_called()

def test_approve_empty_reply(monkeypatch):
    ticket = Ticket(
        id=1,
        review_status="pending_review",
    )

    session = MagicMock()
    session.get.return_value = ticket
    session.__enter__.return_value = session

    monkeypatch.setattr(database, "SessionLocal", lambda: session)

    with pytest.raises(ValueError, match="Approved reply cannot be empty"):
        database.approve_ticket_reply(1, 100, "   ")

    assert ticket.review_status == "pending_review"
    session.commit.assert_not_called()

def test_reject_ticket_reply(monkeypatch):
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

    result = database.reject_ticket_reply(1, 100)

    assert result.review_status == "rejected"
    assert result.reviewed_by == 100
    assert result.reviewed_at is not None

    session.commit.assert_called_once()


def test_reject_already_approved_ticket(monkeypatch):
    ticket = Ticket(
        id=1,
        review_status="approved",
    )

    session = MagicMock()
    session.get.return_value = ticket
    session.__enter__.return_value = session

    monkeypatch.setattr(
        database, "SessionLocal", lambda: session
    )

    with pytest.raises(
        ValueError, match="Ticket is not pending review"
    ):
        database.reject_ticket_reply(1, 100)

    session.commit.assert_not_called()