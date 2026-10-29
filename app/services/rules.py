
from app.schemas.classification import TicketCategory, TicketPriority


def determine_priority(
    category: TicketCategory,
    message_text: str,
) -> TicketPriority:
    """Determine ticket priority using simple business rules."""

    text = message_text.lower()

    critical_keywords = [
        "fraud",
        "unauthorized payment",
        "account hacked",
        "stolen account",
    ]

    high_keywords = [
        "charged twice",
        "double charge",
        "payment failed",
        "cannot access my account",
        "can't access my account",
        "несанкционирован",
        "списали дважды",
        "двойное списание",
        "взломали аккаунт",
        "не могу войти",
    ]

    if any(keyword in text for keyword in critical_keywords):
        return TicketPriority.CRITICAL

    if any(keyword in text for keyword in high_keywords):
        return TicketPriority.HIGH

    if category in {
        TicketCategory.PAYMENT_ISSUE,
        TicketCategory.ACCOUNT_ACCESS,
        TicketCategory.COMPLAINT,
    }:
        return TicketPriority.MEDIUM

    return TicketPriority.LOW


def requires_human_review(
    category: TicketCategory,
    priority: TicketPriority,
) -> bool:
    """Determine whether a ticket must be reviewed by a human."""

    if priority == TicketPriority.CRITICAL:
        return True

    if category in {
        TicketCategory.PAYMENT_ISSUE,
        TicketCategory.RETURN_REFUND,
        TicketCategory.COMPLAINT,
    }:
        return True

    return False
