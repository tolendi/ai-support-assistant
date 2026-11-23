
import re


SENSITIVE_REQUEST_PATTERNS = [
    r"(?<!never )(?<!not )\b(?:send|provide|share|enter)\b.{0,80}\b(?:cvv|cvc|pin|password)\b",
    r"\b(?:cvv|cvc|pin|password)\b.{0,80}\b(?:send|provide|share|enter)\b",
    r"(?:пришлите|укажите|сообщите|отправьте|введите).{0,80}(?:cvv|cvc|пин-код|пароль)",
    r"(?:cvv|cvc|пин-код|пароль).{0,80}(?:пришлите|укажите|сообщите|отправьте|введите)",
]


def contains_sensitive_data_request(reply: str) -> bool:
    """Check whether a reply requests sensitive credentials."""

    return any(
        re.search(pattern, reply, flags=re.IGNORECASE | re.DOTALL)
        for pattern in SENSITIVE_REQUEST_PATTERNS
    )
