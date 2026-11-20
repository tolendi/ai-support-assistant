
import pytest

from app.schemas.classification import TicketCategory
from app.services.missing_information import (
    get_required_information,
    detect_missing_information,
)


def test_get_required_information():
    result = get_required_information(
        TicketCategory.PAYMENT_ISSUE
    )

    assert result == [
        "order_id",
        "payment_date",
        "payment_amount",
    ]


@pytest.mark.parametrize(
    "message,expected",
    [
        (
            "У меня дважды списали деньги.",
            ["order_id", "payment_date", "payment_amount"],
        ),
        (
            "Дважды списали деньги за заказ #12345.",
            ["payment_date", "payment_amount"],
        ),
        (
            "Заказ #12345, оплата 19.11.2026.",
            ["payment_amount"],
        ),
        (
            "Заказ #12345, оплата 19.11.2026, 5000 тенге.",
            [],
        ),
        (
            "Order #12345, payment date 2026-11-19, $50.",
            [],
        ),
        (
            "Тапсырыс №12345, 19.11.2026, 5000 теңге.",
            [],
        ),
    ],
)
def test_detect_missing_payment_information(
    message, expected
):
    result = detect_missing_information(
        message,
        TicketCategory.PAYMENT_ISSUE,
    )

    assert result == expected


@pytest.mark.parametrize(
    "message,expected",
    [
        ("Where is my order?", ["order_id"]),
        ("Where is my order #12345?", []),
        ("Где мой заказ?", ["order_id"]),
        ("Где мой заказ №12345?", []),
        ("Менің тапсырысым қайда?", ["order_id"]),
        ("Тапсырыс №12345 қайда?", []),
    ],
)
def test_detect_missing_order_information(
    message, expected
):
    result = detect_missing_information(
        message,
        TicketCategory.ORDER_STATUS,
    )

    assert result == expected


def test_required_information_is_not_modified():
    result = get_required_information(
        TicketCategory.ORDER_STATUS
    )

    result.clear()

    assert get_required_information(
        TicketCategory.ORDER_STATUS
    ) == ["order_id"]
