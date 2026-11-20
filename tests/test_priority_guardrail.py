
import pytest

from app.schemas.classification import (
    TicketCategory,
    TicketPriority,
)
from app.services.rules import resolve_priority
from app.services import classifier


@pytest.mark.parametrize(
    "rule_priority,llm_priority,expected",
    [
        (TicketPriority.HIGH, TicketPriority.LOW,
         TicketPriority.HIGH),

        (TicketPriority.HIGH, TicketPriority.MEDIUM,
         TicketPriority.HIGH),

        (TicketPriority.CRITICAL, TicketPriority.LOW,
         TicketPriority.CRITICAL),

        (TicketPriority.LOW, TicketPriority.HIGH,
         TicketPriority.HIGH),

        (TicketPriority.MEDIUM, TicketPriority.MEDIUM,
         TicketPriority.MEDIUM),
    ],
)
def test_resolve_priority(
    rule_priority, llm_priority, expected
):
    assert resolve_priority(
        rule_priority,
        llm_priority,
    ) == expected


def test_llm_cannot_lower_priority(monkeypatch):
    monkeypatch.setattr(
        classifier,
        "classify_with_llm",
        lambda text: (
            TicketCategory.PAYMENT_ISSUE,
            TicketPriority.LOW,
        ),
    )

    monkeypatch.setattr(
        classifier,
        "generate_reply",
        lambda **kwargs: "Test reply",
    )

    result = classifier.classify_ticket(
        "За заказ #78945 у меня дважды списали 18000 тенге."
    )

    assert result.category == TicketCategory.PAYMENT_ISSUE
    assert result.priority == TicketPriority.HIGH


@pytest.mark.parametrize(
    "message",
    [
        "У меня дважды списали деньги.",
        "У меня списали дважды.",
        "I was charged twice.",
        "Менің шотымнан ақша екі рет алынды.",
    ],
)
def test_double_charge_rules(message):
    result = classifier.classify_ticket_by_rules(message)

    assert result.category == TicketCategory.PAYMENT_ISSUE
    assert result.priority == TicketPriority.HIGH
