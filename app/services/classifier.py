
from app.schemas.classification import (
    ClassificationResult,
    TicketCategory,
)
from app.services.rules import (
    determine_priority,
    requires_human_review,
)


def classify_ticket(message_text: str) -> ClassificationResult:
    """Classify a support ticket using simple keyword rules."""

    text = message_text.lower()

    if any(word in text for word in [
        "fraud",
        "unauthorized payment",
        "charged twice",
        "double charge",
        "payment failed",
        "списали дважды",
        "двойное списание",
        "несанкционирован",
    ]):
        category = TicketCategory.PAYMENT_ISSUE

    elif any(word in text for word in [
        "delivery",
        "shipment",
        "where is my order",
        "tracking",
        "доставка",
        "где мой заказ",
    ]):
        category = TicketCategory.DELIVERY_ISSUE

    elif any(word in text for word in [
        "refund",
        "return",
        "money back",
        "возврат",
        "вернуть деньги",
    ]):
        category = TicketCategory.RETURN_REFUND

    elif any(word in text for word in [
        "can't log in",
        "cannot log in",
        "can't access my account",
        "password",
        "не могу войти",
        "пароль",
    ]):
        category = TicketCategory.ACCOUNT_ACCESS

    elif any(word in text for word in [
        "complaint",
        "terrible service",
        "unacceptable",
        "жалоба",
        "ужасный сервис",
    ]):
        category = TicketCategory.COMPLAINT

    elif any(word in text for word in [
        "price",
        "color",
        "size",
        "product information",
        "цена",
        "цвет",
        "размер",
    ]):
        category = TicketCategory.PRODUCT_QUESTION

    elif any(word in text for word in [
        "payment",
        "charged",
        "billing",
        "оплата",
        "списание",
    ]):
        category = TicketCategory.PAYMENT_ISSUE

    elif any(word in text for word in [
        "order status",
        "order status update",
        "статус заказа",
    ]):
        category = TicketCategory.ORDER_STATUS

    else:
        category = TicketCategory.OTHER

    priority = determine_priority(category, message_text)
    human_review = requires_human_review(category, priority)

    return ClassificationResult(
        category=category,
        priority=priority,
        confidence=0.70,
        reason="Category and priority assigned using keyword rules.",
        missing_information=[],
        knowledge_article_ids=[],
        draft_reply=(
            "Thank you for contacting support. "
            "We will review your request and get back to you."
        ),
        requires_human_review=human_review,
    )
