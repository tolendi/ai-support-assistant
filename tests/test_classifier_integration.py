
from app.services import classifier
from app.schemas.classification import (
    TicketCategory,
    TicketPriority,
)


def test_classifier_with_llm_reply(monkeypatch):
    monkeypatch.setattr(
        classifier,
        "classify_with_llm",
        lambda text: (
            TicketCategory.PAYMENT_ISSUE,
            TicketPriority.HIGH,
        ),
    )

    expected_reply = (
        "Пожалуйста, уточните дату и сумму платежа."
    )

    monkeypatch.setattr(
        classifier,
        "generate_reply",
        lambda **kwargs: expected_reply,
    )

    result = classifier.classify_ticket(
        "У меня двойное списание за заказ #12345"
    )

    assert result.category == TicketCategory.PAYMENT_ISSUE
    assert result.priority == TicketPriority.HIGH
    assert result.missing_information == [
        "payment_date",
        "payment_amount",
    ]
    assert result.draft_reply == expected_reply
    assert result.requires_human_review is True


def test_classifier_without_llm(monkeypatch):
    def raise_error(*args, **kwargs):
        raise ConnectionError("LLM unavailable")

    monkeypatch.setattr(
        classifier,
        "classify_with_llm",
        raise_error,
    )

    monkeypatch.setattr(
        "app.services.reply_generator.generate_llm_reply",
        raise_error_for_reply,
    )

    result = classifier.classify_ticket(
        "У меня двойное списание за заказ #12345"
    )

    assert result.category == TicketCategory.PAYMENT_ISSUE
    assert result.priority == TicketPriority.HIGH
    assert result.missing_information == [
        "payment_date",
        "payment_amount",
    ]
    assert result.draft_reply == (
        "Здравствуйте! Спасибо за ваше обращение. "
        "Наш специалист рассмотрит ваш вопрос."
    )
    assert result.requires_human_review is True


def raise_error_for_reply(**kwargs):
    raise ValueError("LLM unavailable")
