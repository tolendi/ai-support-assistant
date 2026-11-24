import httpx
import os
from app.schemas.classification import TicketCategory, TicketPriority
from dotenv import load_dotenv

LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL",
    "http://localhost:1235/v1",
)

LLM_CLASSIFIER_MODEL = os.getenv(
    "LLM_CLASSIFIER_MODEL",
    "qwen3-4b",
)

LLM_CLASSIFIER_TEMPERATURE = float(
    os.getenv("LLM_CLASSIFIER_TEMPERATURE", "0")
)

LLM_CLASSIFIER_MAX_TOKENS = int(
    os.getenv("LLM_CLASSIFIER_MAX_TOKENS", "150")
)

def classify_with_llm(message_text: str) -> tuple[TicketCategory, TicketPriority]:
    """Classify a support ticket using a local LLM."""

    response = httpx.post(
        f"{LLM_BASE_URL.rstrip('/')}/chat/completions",
        json={
            "model": LLM_CLASSIFIER_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a customer support ticket classifier. "
                        "Return ONLY valid JSON with exactly two fields: category and priority. "
                        "Allowed categories: payment_issue, order_status, delivery_issue, "
                        "return_refund, account_access, product_question, complaint, other. "
                        "Allowed priorities: critical, high, medium, low. "
                        "Use exact lowercase values from these lists."
                    ),
                },
                {
                    "role": "user",
                    "content": f"/no_think\n{message_text}",
                },
            ],
            "temperature": LLM_CLASSIFIER_TEMPERATURE,
            "max_tokens": LLM_CLASSIFIER_MAX_TOKENS,
        },
        timeout=10,
    )

    response.raise_for_status()

    result = response.json()
    content = result["choices"][0]["message"]["content"]

    import json
    classification = json.loads(content)

    category = TicketCategory(classification["category"])
    priority = TicketPriority(classification["priority"])

    return category, priority
