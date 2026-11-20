
from app.services.reply_generator import generate_reply
from app.schemas.classification import (
    TicketCategory,
    TicketPriority,
)

messages = [
    "У меня дважды списали деньги.",
    "У меня дважды списали деньги за заказ #12345.",
    "Заказ #12345, оплата 19.11.2026.",
    "Заказ #12345, оплата 19.11.2026, 5000 тенге.",
]

for message in messages:
    reply = generate_reply(
        message_text=message,
        category=TicketCategory.PAYMENT_ISSUE,
        priority=TicketPriority.HIGH,
    )

    print(f"Customer: {message}")
    print(f"AI reply: {reply}")
    print("-" * 50)
