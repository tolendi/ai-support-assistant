
from app.schemas.classification import TicketCategory, TicketPriority


DOUBLE_CHARGE_KEYWORDS = (
    "charged twice",
    "double charge",
    "double billing",
    "списали дважды",
    "дважды списали",
    "двойное списание",
    "два раза списали",
    "списали два раза",
    "ақша екі рет алынды",
    "екі рет ақша алынды",
)


PRIORITY_RANK = {
    TicketPriority.LOW: 0,
    TicketPriority.MEDIUM: 1,
    TicketPriority.HIGH: 2,
    TicketPriority.CRITICAL: 3,
}


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
        *DOUBLE_CHARGE_KEYWORDS,
        "payment failed",
        "cannot access my account",
        "can't access my account",
        "несанкционирован",
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


def resolve_priority(
    rule_priority: TicketPriority,
    llm_priority: TicketPriority,
) -> TicketPriority:
    """Prevent LLM from lowering rule-based priority."""

    return max(
        rule_priority,
        llm_priority,
        key=lambda priority: PRIORITY_RANK[priority],
    )
