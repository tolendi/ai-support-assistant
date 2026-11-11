import httpx

from app.schemas.classification import TicketCategory, TicketPriority


def classify_with_llm(message_text: str) -> tuple[TicketCategory, TicketPriority]:
    """Classify a support ticket using a local LLM."""

    response = httpx.post(
        "http://localhost:1235/v1/chat/completions",
        json={
            "model": "qwen3-1.7b",
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
            "temperature": 0,
            "max_tokens": 150,
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
