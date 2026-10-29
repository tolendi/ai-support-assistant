
from fastapi.testclient import TestClient

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

