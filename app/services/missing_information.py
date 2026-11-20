import re
from app.schemas.classification import TicketCategory


REQUIRED_INFORMATION = {
    TicketCategory.PAYMENT_ISSUE: [
        "order_id",
        "payment_date",
        "payment_amount",
    ],
    TicketCategory.ORDER_STATUS: [
        "order_id",
    ],
    TicketCategory.DELIVERY_ISSUE: [
        "order_id",
        "tracking_number",
    ],
    TicketCategory.RETURN_REFUND: [
        "order_id",
        "return_reason",
    ],
    TicketCategory.ACCOUNT_ACCESS: [
        "error_description",
    ],
    TicketCategory.PRODUCT_QUESTION: [
        "product_name",
    ],
    TicketCategory.COMPLAINT: [
        "incident_details",
    ],
    TicketCategory.OTHER: [
        "additional_details",
    ],
}


INFORMATION_PATTERNS = {
    "order_id": (
        r"(?:order|заказ|тапсырыс)"
        r"\s*(?:id|number|номер|нөмірі|№|#)?"
        r"\s*[:#-]?\s*\d+"
    ),
    "payment_date": (
        r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b"
        r"|\b\d{4}-\d{2}-\d{2}\b"
    ),
    "payment_amount": (
        r"\d+(?:[.,]\d+)?\s*"
        r"(?:₸|тенге|теңге|kzt|usd|рублей|руб|₽|\$|eur|€)"
        r"|[$€₸₽]\s*\d+(?:[.,]\d+)?"
    ),
    "tracking_number": (
        r"(?:tracking|трек|трекинг)"
        r"\s*(?:number|номер|№|#)?"
        r"\s*[:-]?\s*[a-z0-9-]{6,}"
    ),
}


def get_required_information(
    category: TicketCategory,
) -> list[str]:
    """Return required information for a ticket category."""

    return REQUIRED_INFORMATION.get(category, []).copy()


def detect_missing_information(
    message_text: str,
    category: TicketCategory,
) -> list[str]:
    """Detect missing information in a customer message."""

    required_fields = get_required_information(category)
    missing_fields = []

    for field in required_fields:
        pattern = INFORMATION_PATTERNS.get(field)

        if pattern is None:
            missing_fields.append(field)
            continue

        if not re.search(
            pattern,
            message_text,
            re.IGNORECASE,
        ):
            missing_fields.append(field)

    return missing_fields
