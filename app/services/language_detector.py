
from lingua import Language, LanguageDetectorBuilder


detector = LanguageDetectorBuilder.from_languages(
    Language.RUSSIAN,
    Language.ENGLISH,
    Language.KAZAKH,
).build()


LANGUAGE_CODES = {
    Language.RUSSIAN: "ru",
    Language.ENGLISH: "en",
    Language.KAZAKH: "kk",
}


def detect_language(message_text: str) -> str:
    """Detect the customer's language."""

    if not message_text.strip():
        return "en"

    language = detector.detect_language_of(message_text)

    return LANGUAGE_CODES.get(language, "en")
