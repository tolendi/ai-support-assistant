
from fastapi import FastAPI

from app.database import save_ticket
from app.models import Ticket
from app.schemas.ticket import TicketCreate
from app.schemas.classification import ClassificationResult
from app.services.classifier import classify_ticket


app = FastAPI(
    title="AI Support Assistant",
    description="API for classifying customer support tickets",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/tickets/classify", response_model=ClassificationResult)
def classify_support_ticket(ticket: TicketCreate):
    # 1. Classify the incoming message.
    result = classify_ticket(ticket.message_text)

    # 2. Create a database record.
    db_ticket = Ticket(
        message_id=ticket.message_id,
        user_id=ticket.user_id,
        message_text=ticket.message_text,
        category=result.category.value,
        priority=result.priority.value,
        confidence=result.confidence,
        reason=result.reason,
        draft_reply=result.draft_reply,
        requires_human_review=result.requires_human_review,
    )

    # 3. Save the ticket in PostgreSQL.
    save_ticket(db_ticket)

    # 4. Return the classification result.
    return result
