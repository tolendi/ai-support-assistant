import httpx
import os
import secrets

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request, Header
from app.database import save_ticket, get_ticket_by_id, get_tickets, update_ticket_status, get_ticket_status_history, update_reply_status
from app.models import Ticket
from app.schemas.ticket import TicketCreate
from app.schemas.ticket_response import TicketResponse
from app.schemas.ticket_status import TicketStatusUpdate
from app.schemas.ticket_history import TicketStatusHistoryResponse
from app.schemas.classification import ClassificationResult
from app.services.classifier import classify_ticket
from app.telegram_client import get_bot_info, parse_telegram_message, send_telegram_message
from app.schemas.telegram import TelegramWebhookRequest
from sqlalchemy.exc import IntegrityError

load_dotenv()

TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET")

if not TELEGRAM_WEBHOOK_SECRET:
    raise RuntimeError("TELEGRAM_WEBHOOK_SECRET is not set")


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
    try:
        save_ticket(db_ticket)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to save ticket",
        )

    # 4. Return the classification result.
    return result


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int):
    ticket = get_ticket_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


@app.get("/tickets", response_model=list[TicketResponse])
def list_tickets(
    category: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    tickets = get_tickets(
        category=category,
        priority=priority,
        status=status,
        limit=limit,
        offset=offset,
    )
    return tickets


@app.patch(
    "/tickets/{ticket_id}/status",
    response_model=TicketResponse,
)
def change_ticket_status(
    ticket_id: int,
    status_update: TicketStatusUpdate,
):
    try:
        ticket = update_ticket_status(
            ticket_id=ticket_id,
            status=status_update.status.value,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


@app.get(
    "/tickets/{ticket_id}/history",
    response_model=list[TicketStatusHistoryResponse],
)
def get_ticket_history(ticket_id: int):
    history = get_ticket_status_history(ticket_id)

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return history


@app.post("/telegram/webhook")
async def telegram_webhook(
    update: TelegramWebhookRequest,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if not secrets.compare_digest(
        x_telegram_bot_api_secret_token or "",
        TELEGRAM_WEBHOOK_SECRET,
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid Telegram webhook secret",
        )
    message = parse_telegram_message(update.model_dump())

    if message is None:
        return {"ok": True, "message": "Update ignored"}
    
    classification = classify_ticket(message["text"])

    ticket = Ticket(
        telegram_update_id=update.update_id,
        message_id=message["message_id"],
        user_id=message["user_id"],
        message_text=message["text"],
        category=classification.category.value,
        priority=classification.priority.value,
        confidence=classification.confidence,
        reason=classification.reason,
        draft_reply=classification.draft_reply,
        requires_human_review=classification.requires_human_review,
    )

    try:
        saved_ticket = save_ticket(ticket)
    except IntegrityError:
        return {
            "ok": True,
            "message": "Duplicate update ignored",
        }

    try:
        send_telegram_message(
            chat_id=message["chat_id"],
            text=classification.draft_reply,
        )

    except httpx.HTTPError as error:
        print(f"Failed to send Telegram reply: {error}")

        update_reply_status(
            ticket_id=saved_ticket.id,
            reply_status="failed",
        )

    else:
        update_reply_status(
            ticket_id=saved_ticket.id,
            reply_status="sent",
        )

    print("Classification:", classification.model_dump())

    return {
        "ok": True,
        "message": "Telegram message received",
        "ticket_id": saved_ticket.id,
        "data": message,
        "classification": classification.model_dump(mode="json"),
    }