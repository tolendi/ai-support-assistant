
import pytest

from app.services.reply_guardrails import (
    contains_sensitive_data_request,
)


@pytest.mark.parametrize(
    "reply",
    [
        "Please provide your CVV.",
        "Send us your account password.",
        "Enter your PIN to continue.",
        "Пожалуйста, пришлите ваш CVV.",
        "Сообщите пароль для подтверждения.",
    ],
)
def test_detects_sensitive_requests(reply):
    assert contains_sensitive_data_request(reply) is True


@pytest.mark.parametrize(
    "reply",
    [
        "Please provide your order number.",
        "Could you share the payment date?",
        "Укажите номер заказа.",
        "Наш специалист рассмотрит ваше обращение.",
    ],
)
def test_allows_safe_replies(reply):
    assert contains_sensitive_data_request(reply) is False


def test_unsafe_llm_reply_uses_fallback(monkeypatch):
    from app.services import reply_generator
    from app.schemas.classification import (
        TicketCategory,
        TicketPriority,
    )
    from app.services.reply_templates import get_fallback_reply

    def fake_llm(**kwargs):
        return "Please provide your CVV to complete the refund."

    monkeypatch.setattr(
        reply_generator,
        "generate_llm_reply",
        fake_llm,
    )

    result = reply_generator.generate_reply(
        message_text="I was charged twice",
        category=TicketCategory.PAYMENT_ISSUE,
        priority=TicketPriority.HIGH,
        articles=[
            {
                "id": 1,
                "title": "Payment problems",
                "content": "Collect the order number.",
            }
        ],
    )

    assert result == get_fallback_reply("en")
    assert "CVV" not in result


@pytest.mark.parametrize(
    "reply",
    [
        "Never provide your password to anyone.",
        "Do not share your CVV with support agents.",
        "Никогда не сообщайте свой пароль.",
        "Не отправляйте CVV сотрудникам поддержки.",
        "Please provide your order number.",
    ],
)
def test_safe_security_warnings_are_allowed(reply):
    assert contains_sensitive_data_request(reply) is False
