import httpx

from app.database import (
    prepare_approved_reply,
    finish_approved_reply,
)
from app.telegram_client import send_telegram_message


def send_approved_reply(ticket_id: int):
    ticket = prepare_approved_reply(ticket_id)

    if ticket is None:
        return None

    try:
        response = send_telegram_message(
            chat_id=ticket.chat_id,
            text=ticket.approved_reply,
        )

        if response.get("ok") is True:
            delivery_status = "sent"
        elif response.get("ok") is False:
            delivery_status = "failed"
        else:
            delivery_status = "unknown"

    except httpx.HTTPStatusError as error:
        if 400 <= error.response.status_code < 500:
            delivery_status = "failed"
        else:
            delivery_status = "unknown"

    except (httpx.RequestError, ValueError):
        delivery_status = "unknown"

    return finish_approved_reply(
        ticket_id=ticket_id,
        delivery_status=delivery_status,
    )