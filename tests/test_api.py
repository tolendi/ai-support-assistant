
from fastapi.testclient import TestClient

from app.main import app


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
