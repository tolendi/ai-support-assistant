
from app.schemas.classification import TicketCategory, TicketPriority
from app.services.rules import determine_priority, requires_human_review


def test_critical_keyword_sets_critical_priority():
    result = determine_priority(
        TicketCategory.OTHER,
        "I suspect fraud on my account",
    )

    assert result == TicketPriority.CRITICAL


def test_double_charge_sets_high_priority():
    result = determine_priority(
        TicketCategory.PAYMENT_ISSUE,
        "I was charged twice",
    )

    assert result == TicketPriority.HIGH


def test_product_question_has_low_priority():
    result = determine_priority(
        TicketCategory.PRODUCT_QUESTION,
        "What color is this product?",
    )

    assert result == TicketPriority.LOW


def test_payment_issue_requires_human_review():
    result = requires_human_review(
        TicketCategory.PAYMENT_ISSUE,
        TicketPriority.MEDIUM,
    )

    assert result is True


def test_critical_ticket_requires_human_review():
    result = requires_human_review(
        TicketCategory.OTHER,
        TicketPriority.CRITICAL,
    )

    assert result is True


def test_product_question_does_not_require_human_review():
    result = requires_human_review(
        TicketCategory.PRODUCT_QUESTION,
        TicketPriority.LOW,
    )

    assert result is False
