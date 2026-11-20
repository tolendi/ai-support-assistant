
FALLBACK_REPLIES = {
    "ru": (
        "Здравствуйте! Спасибо за ваше обращение. "
        "Наш специалист рассмотрит ваш вопрос."
    ),
    "en": (
        "Hello! Thank you for contacting support. "
        "Our specialist will review your request."
    ),
    "kk": (
        "Сәлеметсіз бе! Хабарласқаныңызға рақмет. "
        "Маманымыз өтінішіңізді қарайды."
    ),
}


def get_fallback_reply(language: str) -> str:
    return FALLBACK_REPLIES.get(
        language,
        FALLBACK_REPLIES["en"],
    )
