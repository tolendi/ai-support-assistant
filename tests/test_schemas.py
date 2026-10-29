
import pytest
from pydantic import ValidationError

from app.schemas.ticket import TicketCreate


def test_valid_ticket():
    ticket = TicketCreate(
        message_id=125,
        user_id=78901,
        message_text="I was charged twice!",
    )

    assert ticket.message_id == 125
    assert ticket.user_id == 78901
    assert ticket.message_text == "I was charged twice!"


def test_empty_message_is_rejected():
    with pytest.raises(ValidationError):
        TicketCreate(
            message_id=125,
            user_id=78901,
            message_text="   ",
        )


def test_negative_user_id_is_rejected():
    with pytest.raises(ValidationError):
        TicketCreate(
            message_id=125,
            user_id=-1,
            message_text="Where is my order?",
        )


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError):
        TicketCreate(
            message_id=125,
            user_id=78901,
            message_text="Where is my order?",
            priority="critical",
        )


def test_message_is_stripped():
    ticket = TicketCreate(
        message_id=125,
        user_id=78901,
        message_text="  Where is my order?  ",
    )

    assert ticket.message_text == "Where is my order?"
