import httpx

from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from app.main import app
from app import main


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_classify_ticket_endpoint():
    response = client.post(
        "/tickets/classify",
        json={
            "message_id": 125,
            "user_id": 78901,
            "message_text": "I was charged twice",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "payment_issue"
    assert data["priority"] == "high"
    assert data["requires_human_review"] is True


def test_classify_ticket_rejects_empty_message():
    response = client.post(
        "/tickets/classify",
        json={
            "message_id": 126,
            "user_id": 78901,
            "message_text": "   ",
        },
    )

    assert response.status_code == 422


def test_classify_ticket_rejects_unknown_field():
    response = client.post(
        "/tickets/classify",
        json={
            "message_id": 127,
            "user_id": 78901,
            "message_text": "Where is my order?",
            "unexpected_field": "value",
        },
    )

    assert response.status_code == 422


    
def test_classify_ticket_saves_ticket(monkeypatch):
    saved_tickets = []

    def fake_save_ticket(ticket):
        saved_tickets.append(ticket)
        return ticket

    monkeypatch.setattr(main, "save_ticket", fake_save_ticket)

    response = client.post(
        "/tickets/classify",
        json={
            "message_id": 987654,
            "user_id": 123456,
            "message_text": "I was charged twice for my order",
        },
    )

    assert response.status_code == 200
    assert len(saved_tickets) == 1

    saved_ticket = saved_tickets[0]

    assert saved_ticket.message_id == 987654
    assert saved_ticket.user_id == 123456
    assert saved_ticket.message_text == "I was charged twice for my order"
    assert saved_ticket.category == "payment_issue"
    assert saved_ticket.priority == "high"



def test_classify_ticket_returns_error_when_saving_fails(monkeypatch):
    def fake_save_ticket(ticket):
        raise RuntimeError("Database unavailable")

    monkeypatch.setattr(main, "save_ticket", fake_save_ticket)

    response = client.post(
        "/tickets/classify",
        json={
            "message_id": 987655,
            "user_id": 123456,
            "message_text": "I was charged twice for my order",
        },
    )

    assert response.status_code == 500


def test_get_ticket_by_id(monkeypatch):
    from types import SimpleNamespace

    fake_ticket = SimpleNamespace(
        id=3,
        message_id=125,
        user_id=78901,
        message_text="I was charged twice",
        category="payment_issue",
        priority="high",
        confidence=0.7,
        reason="Keyword-based classification",
        draft_reply="We will review your request.",
        requires_human_review=True,
        status="new",
        created_at="2026-10-29T10:00:00+00:00",
    )

    def fake_get_ticket_by_id(ticket_id):
        return fake_ticket

    monkeypatch.setattr(main, "get_ticket_by_id", fake_get_ticket_by_id)

    response = client.get("/tickets/3")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 3
    assert data["category"] == "payment_issue"
    assert data["priority"] == "high"
    assert data["status"] == "new"


def test_get_ticket_not_found(monkeypatch):
    def fake_get_ticket_by_id(ticket_id):
        return None

    monkeypatch.setattr(main, "get_ticket_by_id", fake_get_ticket_by_id)

    response = client.get("/tickets/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_get_ticket_rejects_invalid_id():
    response = client.get("/tickets/abc")

    assert response.status_code == 422

def test_get_tickets(monkeypatch):
    from types import SimpleNamespace

    fake_tickets = [
        SimpleNamespace(
            id=3,
            message_id=125,
            user_id=78901,
            message_text="I was charged twice",
            category="payment_issue",
            priority="high",
            confidence=0.7,
            reason="Keyword-based classification",
            draft_reply="We will review your request.",
            requires_human_review=True,
            status="new",
            created_at="2026-10-29T10:00:00+00:00",
        )
    ]

    def fake_get_tickets(category=None, 
                         priority=None, 
                         status=None,
                         limit=50,
                         offset=0,
    ):
        return fake_tickets

    monkeypatch.setattr(main, "get_tickets", fake_get_tickets)

    response = client.get("/tickets")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "payment_issue"


def test_get_tickets_empty(monkeypatch):
    def fake_get_tickets(
            category=None, 
            priority=None, 
            status=None,
            limit=50,
            offset=0,
    ):
        return []

    monkeypatch.setattr(main, "get_tickets", fake_get_tickets)

    response = client.get("/tickets")

    assert response.status_code == 200
    assert response.json() == []



def test_get_tickets_with_filters(monkeypatch):
    from types import SimpleNamespace

    captured_filters = {}

    def fake_get_tickets(category=None, 
                         priority=None, 
                         status=None,
                         limit=50,
                         offset=0,
    ):
        captured_filters["category"] = category
        captured_filters["priority"] = priority
        captured_filters["status"] = status

        return [
            SimpleNamespace(
                id=3,
                message_id=125,
                user_id=78901,
                message_text="I was charged twice",
                category="payment_issue",
                priority="high",
                confidence=0.7,
                reason="Keyword-based classification",
                draft_reply="We will review your request.",
                requires_human_review=True,
                status="new",
                created_at="2026-10-29T10:00:00+00:00",
            )
        ]

    monkeypatch.setattr(main, "get_tickets", fake_get_tickets)

    response = client.get(
        "/tickets?category=payment_issue&priority=high&status=new"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1

    assert captured_filters["category"] == "payment_issue"
    assert captured_filters["priority"] == "high"
    assert captured_filters["status"] == "new"


def test_get_tickets_with_pagination(monkeypatch):
    from types import SimpleNamespace

    captured_params = {}

    def fake_get_tickets(
        category=None,
        priority=None,
        status=None,
        limit=50,
        offset=0,
    ):
        captured_params["limit"] = limit
        captured_params["offset"] = offset
        return []

    monkeypatch.setattr(main, "get_tickets", fake_get_tickets)

    response = client.get("/tickets?limit=10&offset=20")

    assert response.status_code == 200
    assert captured_params["limit"] == 10
    assert captured_params["offset"] == 20


def test_get_tickets_rejects_invalid_limit():
    response = client.get("/tickets?limit=0")

    assert response.status_code == 422


def test_get_tickets_rejects_negative_offset():
    response = client.get("/tickets?offset=-1")

    assert response.status_code == 422


def test_update_ticket_status(monkeypatch):
    from types import SimpleNamespace

    updated_tickets = {}

    def fake_update_ticket_status(ticket_id, status):
        updated_tickets["ticket_id"] = ticket_id
        updated_tickets["status"] = status

        return SimpleNamespace(
            id=ticket_id,
            message_id=125,
            user_id=78901,
            message_text="I was charged twice",
            category="payment_issue",
            priority="high",
            confidence=0.7,
            reason="Keyword-based classification",
            draft_reply="We will review your request.",
            requires_human_review=True,
            status=status,
            created_at="2026-10-29T10:00:00+00:00",
        )

    monkeypatch.setattr(
        main,
        "update_ticket_status",
        fake_update_ticket_status,
    )

    response = client.patch(
        "/tickets/1/status",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    assert updated_tickets["ticket_id"] == 1
    assert updated_tickets["status"] == "in_progress"


def test_update_ticket_status_not_found(monkeypatch):
    def fake_update_ticket_status(ticket_id, status):
        return None

    monkeypatch.setattr(
        main,
        "update_ticket_status",
        fake_update_ticket_status,
    )

    response = client.patch(
        "/tickets/150/status",
        json={"status": "resolved"},
    )

    assert response.status_code == 404


def test_update_ticket_status_invalid(monkeypatch):
    response = client.patch(
        "/tickets/1/status",
        json={"status": "unknown"},
    )

    assert response.status_code == 422


def test_update_ticket_status_creates_history(monkeypatch):
    from types import SimpleNamespace

    saved_history = []

    ticket = SimpleNamespace(
        id=1,
        status="new",
    )

    class FakeSession:
        def get(self, model, ticket_id):
            return ticket

        def add(self, history_entry):
            saved_history.append(history_entry)

        def commit(self):
            pass

        def refresh(self, obj):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    class FakeSessionLocal:
        def __call__(self):
            return FakeSession()

    monkeypatch.setattr(
        "app.database.SessionLocal",
        FakeSessionLocal(),
    )

    from app.database import update_ticket_status

    result = update_ticket_status(1, "in_progress")

    assert result.status == "in_progress"
    assert len(saved_history) == 1
    assert saved_history[0].ticket_id == 1
    assert saved_history[0].old_status == "new"
    assert saved_history[0].new_status == "in_progress"


def test_update_ticket_status_rejects_invalid_transition(monkeypatch):
    def fake_update_ticket_status(ticket_id, status):
        raise ValueError(
            "Status transition from 'in_progress' to 'new' is not allowed"
        )

    monkeypatch.setattr(
        main,
        "update_ticket_status",
        fake_update_ticket_status,
    )

    response = client.patch(
        "/tickets/1/status",
        json={"status": "new"},
    )

    assert response.status_code == 409
    assert "not allowed" in response.json()["detail"]


def test_update_ticket_status_accepts_valid_transition(monkeypatch):
    from types import SimpleNamespace

    def fake_update_ticket_status(ticket_id, status):
        return SimpleNamespace(
            id=ticket_id,
            message_id=125,
            user_id=78901,
            message_text="I was charged twice",
            category="payment_issue",
            priority="high",
            confidence=0.7,
            reason="Keyword-based classification",
            draft_reply="We will review your request.",
            requires_human_review=True,
            status=status,
            created_at="2026-10-29T10:00:00+00:00",
            updated_at="2026-10-29T10:30:00+00:00",
        )

    monkeypatch.setattr(
        main,
        "update_ticket_status",
        fake_update_ticket_status,
    )

    response = client.patch(
        "/tickets/1/status",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_get_ticket_history(monkeypatch):
    from types import SimpleNamespace
    from datetime import datetime, timezone

    history = [
        SimpleNamespace(
            id=1,
            ticket_id=10,
            old_status="new",
            new_status="in_progress",
            changed_at=datetime.now(timezone.utc),
        )
    ]

    def fake_get_history(ticket_id):
        return history

    monkeypatch.setattr(
        main,
        "get_ticket_status_history",
        fake_get_history,
    )

    response = client.get("/tickets/10/history")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["old_status"] == "new"
    assert response.json()[0]["new_status"] == "in_progress"


def test_get_ticket_history_empty(monkeypatch):
    def fake_get_history(ticket_id):
        return []

    monkeypatch.setattr(
        main,
        "get_ticket_status_history",
        fake_get_history,
    )

    response = client.get("/tickets/10/history")

    assert response.status_code == 200
    assert response.json() == []


def test_get_ticket_history_not_found(monkeypatch):
    def fake_get_history(ticket_id):
        return None

    monkeypatch.setattr(
        main,
        "get_ticket_status_history",
        fake_get_history,
    )

    response = client.get("/tickets/999999/history")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_telegram_webhook_duplicate_update(monkeypatch):
    def mock_save_ticket(ticket):
        raise IntegrityError("Duplicate update", {}, Exception())

    def mock_send_telegram_message(chat_id, text):
        raise AssertionError("Telegram reply should not be sent")

    monkeypatch.setattr(main, "save_ticket", mock_save_ticket)
    monkeypatch.setattr(
        main,
        "send_telegram_message",
        mock_send_telegram_message,
    )

    response = client.post(
        "/telegram/webhook",
        json={
            "update_id": 123456,
            "message": {
                "message_id": 100,
                "from": {"id": 789},
                "chat": {"id": 789},
                "text": "I was charged twice",
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Duplicate update ignored"

def test_telegram_webhook_reply_sent(monkeypatch):
    class MockTicket:
        id = 123

    statuses = []

    monkeypatch.setattr(
        main, "save_ticket", lambda ticket: MockTicket()
    )

    monkeypatch.setattr(
        main,
        "send_telegram_message",
        lambda chat_id, text: {"ok": True},
    )

    monkeypatch.setattr(
        main,
        "update_reply_status",
        lambda ticket_id, reply_status: statuses.append(
            (ticket_id, reply_status)
        ),
    )

    response = client.post(
        "/telegram/webhook",
        json={
            "update_id": 987654,
            "message": {
                "message_id": 101,
                "from": {"id": 555},
                "chat": {"id": 555},
                "text": "I was charged twice",
            },
        },
    )

    assert response.status_code == 200
    assert statuses == [(123, "sent")]

def test_telegram_webhook_reply_failed(monkeypatch):
    class MockTicket:
        id = 123

    statuses = []

    def mock_send_telegram_message(chat_id, text):
        raise httpx.RequestError("Connection failed")

    monkeypatch.setattr(
        main, "save_ticket", lambda ticket: MockTicket()
    )

    monkeypatch.setattr(
        main,
        "send_telegram_message",
        mock_send_telegram_message,
    )

    monkeypatch.setattr(
        main,
        "update_reply_status",
        lambda ticket_id, reply_status: statuses.append(
            (ticket_id, reply_status)
        ),
    )

    response = client.post(
        "/telegram/webhook",
        json={
            "update_id": 987655,
            "message": {
                "message_id": 102,
                "from": {"id": 555},
                "chat": {"id": 555},
                "text": "I was charged twice",
            },
        },
    )

    assert response.status_code == 200
    assert statuses == [(123, "failed")]