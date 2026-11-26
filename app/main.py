import httpx
import os
import secrets

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request, Header, Depends
from app.database import reject_ticket_reply, approve_ticket_reply, save_ticket, get_ticket_by_id, get_tickets, update_ticket_status, get_ticket_status_history, update_reply_status
from app.models import Ticket
from app.schemas.ticket import TicketCreate
from app.schemas.ticket_response import TicketResponse
from app.schemas.ticket_status import TicketStatusUpdate
from app.schemas.ticket_history import TicketStatusHistoryResponse
from app.schemas.classification import ClassificationResult
from app.schemas.review import TicketApproveRequest
from app.services.classifier import classify_ticket
from app.services.reply_sender import send_approved_reply
from app.telegram_client import get_bot_info, parse_telegram_message, send_telegram_message, answer_callback_query
from app.schemas.telegram import TelegramWebhookRequest
from sqlalchemy.exc import IntegrityError

load_dotenv()

TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET")


if not TELEGRAM_WEBHOOK_SECRET:
    raise RuntimeError("TELEGRAM_WEBHOOK_SECRET is not set")

OPERATOR_API_KEY = os.getenv("OPERATOR_API_KEY")
OPERATOR_ID = int(os.getenv("OPERATOR_ID", "1"))
OPERATOR_TELEGRAM_ID = int(
    os.getenv("OPERATOR_TELEGRAM_ID", "0")
)

ACKNOWLEDGMENT_REPLY = (
    "Здравствуйте! Ваше обращение принято. "
    "Мы рассмотрим его и вернёмся с ответом."
)

if not OPERATOR_API_KEY:
    raise RuntimeError("OPERATOR_API_KEY is not set")


app = FastAPI(
    title="AI Support Assistant",
    description="API for classifying customer support tickets",
    version="0.1.0",
)

def authorize_operator(
    x_operator_api_key: str | None = Header(default=None),
) -> int:
    if not secrets.compare_digest(
        (x_operator_api_key or "").encode("utf-8"),
        OPERATOR_API_KEY.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid operator API key",
        )

    return OPERATOR_ID

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post(
        "/tickets/classify", 
        response_model=ClassificationResult,
        dependencies=[Depends(authorize_operator)],
)
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
        knowledge_article_ids=result.knowledge_article_ids,
        missing_information=result.missing_information,
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


@app.get(
        "/tickets/{ticket_id}", 
        response_model=TicketResponse,
        dependencies=[Depends(authorize_operator)],
)
def get_ticket(ticket_id: int):
    ticket = get_ticket_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


@app.get(
        "/tickets", 
        response_model=list[TicketResponse],
        dependencies=[Depends(authorize_operator)],
)
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
    dependencies=[Depends(authorize_operator)],
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
    dependencies=[Depends(authorize_operator)],
)
def get_ticket_history(ticket_id: int):
    history = get_ticket_status_history(ticket_id)

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return history

def handle_operator_callback(callback: dict):
    callback_id = callback.get("id")

    if not callback_id:
        return {"ok": True, "message": "Invalid callback"}

    def respond(text):
        try:
            answer_callback_query(callback_id, text)
        except (httpx.HTTPError, ValueError):
            print("Failed to answer Telegram callback")

        return {"ok": True, "message": text}

    telegram_user_id = callback.get("from", {}).get("id")

    if (
        not OPERATOR_TELEGRAM_ID
        or telegram_user_id != OPERATOR_TELEGRAM_ID
    ):
        return respond("Доступ запрещён")

    data = callback.get("data") or ""
    

    try:
        action, raw_ticket_id = data.split(":", 1)
        ticket_id = int(raw_ticket_id)
    except ValueError:
        return respond("Некорректная команда")

    if action not in ("approve", "reject") or ticket_id <= 0:
        return respond("Неизвестное действие")

    ticket = get_ticket_by_id(ticket_id)

    if ticket is None:
        return respond("Заявка не найдена")

    try:
        if action == "approve":
            if ticket.chat_id is None:
                return respond("У заявки отсутствует chat_id")

            approved_ticket = approve_ticket_reply(
                ticket_id=ticket_id,
                operator_id=OPERATOR_ID,
                approved_reply=ticket.draft_reply,
            )

            if approved_ticket is None:
                return respond("Заявка не найдена")

            result = send_approved_reply(ticket_id)

            if result is None:
                return respond("Заявка не найдена")

            if result.approved_reply_status == "sent":
                return respond(
                    "Ответ одобрен и отправлен клиенту"
                )

            return respond(
                "Ответ одобрен. Статус доставки: "
                f"{result.approved_reply_status}"
            )

        if action == "reject":
            rejected_ticket = reject_ticket_reply(
                ticket_id=ticket_id,
                operator_id=OPERATOR_ID,
            )

            if rejected_ticket is None:
                return respond("Заявка не найдена")

            return respond("Ответ отклонён")

    except ValueError:
        return respond(
            "Действие невозможно. Проверьте статус заявки."
        )

@app.post("/telegram/webhook")
def telegram_webhook(
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
    if update.callback_query is not None:
        return handle_operator_callback(update.callback_query)
    message = parse_telegram_message(update.model_dump())

    if message is None:
        return {"ok": True, "message": "Update ignored"}
    
    classification = classify_ticket(message["text"])

    ticket = Ticket(
        telegram_update_id=update.update_id,
        message_id=message["message_id"],
        user_id=message["user_id"],
        chat_id=message["chat_id"],
        message_text=message["text"],
        category=classification.category.value,
        priority=classification.priority.value,
        confidence=classification.confidence,
        reason=classification.reason,
        knowledge_article_ids=classification.knowledge_article_ids,
        missing_information=classification.missing_information,
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
            text=ACKNOWLEDGMENT_REPLY,
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


@app.post("/tickets/{ticket_id}/approve")
def approve_ticket(
    ticket_id: int,
    request: TicketApproveRequest,
    operator_id: int = Depends(authorize_operator),
):
    try:
        ticket = approve_ticket_reply(
            ticket_id=ticket_id,
            operator_id=operator_id,
            approved_reply=request.approved_reply,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return {
        "id": ticket.id,
        "review_status": ticket.review_status,
        "approved_reply": ticket.approved_reply,
        "reviewed_by": ticket.reviewed_by,
        "reviewed_at": ticket.reviewed_at,
    }

@app.post("/tickets/{ticket_id}/send-reply")
def send_ticket_reply(
    ticket_id: int,
    operator_id: int = Depends(authorize_operator),
):
    try:
        ticket = send_approved_reply(ticket_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return {
        "id": ticket.id,
        "review_status": ticket.review_status,
        "approved_reply_status": ticket.approved_reply_status,
        "approved_reply_sent_at": ticket.approved_reply_sent_at,
    }

@app.post("/tickets/{ticket_id}/reject")
def reject_ticket(
    ticket_id: int,
    operator_id: int = Depends(authorize_operator),
):
    try:
        ticket = reject_ticket_reply(
            ticket_id=ticket_id,
            operator_id=operator_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return {
        "id": ticket.id,
        "review_status": ticket.review_status,
        "reviewed_by": ticket.reviewed_by,
        "reviewed_at": ticket.reviewed_at,
    }