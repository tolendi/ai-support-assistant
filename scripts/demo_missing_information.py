
from app.services.missing_information import (
    detect_missing_information,
)
from app.schemas.classification import TicketCategory


messages = [
    "У меня дважды списали деньги.",
    "Дважды списали деньги за заказ #12345.",
    "Заказ #12345, оплата 19.11.2026.",
    "Заказ #12345, оплата 19.11.2026, 5000 тенге.",
]

for message in messages:
    result = detect_missing_information(
        message,
        TicketCategory.PAYMENT_ISSUE,
    )

    print(f"Message: {message}")
    print(f"Missing: {result}")
    print("-" * 50)
