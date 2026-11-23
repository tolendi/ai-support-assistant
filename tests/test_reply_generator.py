
import httpx
import pytest

from app.services import reply_generator
from app.services.reply_templates import get_fallback_reply
from app.schemas.classification import (
    TicketCategory,
    TicketPriority,
)


def test_generate_reply_success(monkeypatch):
    expected_reply = "Please provide your order number."

    monkeypatch.setattr(
        reply_generator,
        "generate_llm_reply",
        lambda **kwargs: expected_reply,
    )

    result = reply_generator.generate_reply(
        message_text="Where is my order?",
        category=TicketCategory.ORDER_STATUS,
        priority=TicketPriority.MEDIUM,
    )

    assert result == expected_reply


@pytest.mark.parametrize(
    "message,language",
    [
        ("Где мой заказ?", "ru"),
        ("Where is my order?", "en"),
        ("Менің тапсырысым қайда?", "kk"),
    ],
)
def test_generate_reply_fallback(
    monkeypatch, message, language
):
    def raise_connection_error(**kwargs):
        raise httpx.ConnectError("LLM unavailable")

    monkeypatch.setattr(
        reply_generator,
        "generate_llm_reply",
        raise_connection_error,
    )

    result = reply_generator.generate_reply(
        message_text=message,
        category=TicketCategory.ORDER_STATUS,
        priority=TicketPriority.MEDIUM,
    )

    assert result == get_fallback_reply(language)


def test_generate_reply_language_mismatch(monkeypatch):
    monkeypatch.setattr(
        reply_generator,
        "generate_llm_reply",
        lambda **kwargs: "Please provide your order number.",
    )

    result = reply_generator.generate_reply(
        message_text="Где мой заказ?",
        category=TicketCategory.ORDER_STATUS,
        priority=TicketPriority.MEDIUM,
    )

    assert result == get_fallback_reply("ru")


@pytest.mark.parametrize(
    "response_data",
    [
        {"choices": [{"message": {"content": ""}}]},
        {"choices": [{"message": {"content": "   "}}]},
        {"choices": [{"message": {"content": None}}]},
        {"choices": []},
        {},
    ],
)
def test_generate_reply_invalid_response(
    monkeypatch, response_data
):
    def mock_post(*args, **kwargs):
        return httpx.Response(
            status_code=200,
            json=response_data,
            request=httpx.Request(
                "POST",
                "http://localhost:1235/v1/chat/completions",
            ),
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    result = reply_generator.generate_reply(
        message_text="Where is my order?",
        category=TicketCategory.ORDER_STATUS,
        priority=TicketPriority.MEDIUM,
    )

    assert result == get_fallback_reply("en")


def test_generate_reply_http_error(monkeypatch):
    def mock_post(*args, **kwargs):
        return httpx.Response(
            status_code=500,
            request=httpx.Request(
                "POST",
                "http://localhost:1235/v1/chat/completions",
            ),
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    result = reply_generator.generate_reply(
        message_text="Where is my order?",
        category=TicketCategory.ORDER_STATUS,
        priority=TicketPriority.MEDIUM,
    )

    assert result == get_fallback_reply("en")


def test_generate_reply_timeout(monkeypatch):
    def mock_post(*args, **kwargs):
        raise httpx.ReadTimeout("Request timed out")

    monkeypatch.setattr(httpx, "post", mock_post)

    result = reply_generator.generate_reply(
        message_text="Где мой заказ?",
        category=TicketCategory.ORDER_STATUS,
        priority=TicketPriority.MEDIUM,
    )

    assert result == get_fallback_reply("ru")


def test_generate_llm_reply_success(monkeypatch):
    expected_reply = "Please provide your order number."

    def mock_post(*args, **kwargs):
        return httpx.Response(
            status_code=200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": expected_reply
                        }
                    }
                ]
            },
            request=httpx.Request(
                "POST",
                "http://localhost:1235/v1/chat/completions",
            ),
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    result = reply_generator.generate_llm_reply(
        message_text="Where is my order?",
        category=TicketCategory.ORDER_STATUS,
        priority=TicketPriority.MEDIUM,
    )

    assert result == expected_reply


def test_no_knowledge_articles_uses_safe_fallback(monkeypatch):
    def forbidden_llm_call(**kwargs):
        raise AssertionError(
            "LLM must not be called without knowledge articles"
        )

    monkeypatch.setattr(
        reply_generator,
        "generate_llm_reply",
        forbidden_llm_call,
    )

    result = reply_generator.generate_reply(
        message_text="Какие у вас часы работы?",
        category=TicketCategory.OTHER,
        priority=TicketPriority.LOW,
        articles=[],
    )

    assert result == get_fallback_reply("ru")
    assert "9:00" not in result
    assert "Московскому" not in result
