
from app.schemas.classification import TicketCategory, TicketPriority
from app.services.classifier import classify_ticket_by_rules


def test_double_charge_is_payment_issue():
    result = classify_ticket_by_rules("I was charged twice")

    assert result.category == TicketCategory.PAYMENT_ISSUE
    assert result.priority == TicketPriority.HIGH
    assert result.requires_human_review is True


def test_delivery_message_is_classified():
    result = classify_ticket_by_rules("Where is my order?")

    assert result.category == TicketCategory.DELIVERY_ISSUE


def test_refund_message_is_classified():
    result = classify_ticket_by_rules("I want a refund")

    assert result.category == TicketCategory.RETURN_REFUND
    assert result.requires_human_review is True


def test_account_access_message_is_classified():
    result = classify_ticket_by_rules("I can't log in to my account")

    assert result.category == TicketCategory.ACCOUNT_ACCESS


def test_product_question_has_low_priority():
    result = classify_ticket_by_rules("What color is this product?")

    assert result.category == TicketCategory.PRODUCT_QUESTION
    assert result.priority == TicketPriority.LOW
    assert result.requires_human_review is False


def test_unknown_message_uses_other_category():
    result = classify_ticket_by_rules("Hello, I have a question")

    assert result.category == TicketCategory.OTHER
