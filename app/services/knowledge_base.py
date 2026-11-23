
import json
import re
from pathlib import Path


KNOWLEDGE_BASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "knowledge_base"
    / "articles.json"
)


def load_articles(path: Path = KNOWLEDGE_BASE_PATH) -> list[dict]:
    """Load articles from the knowledge base."""

    with path.open("r", encoding="utf-8") as file:
        articles = json.load(file)

    if not isinstance(articles, list):
        raise ValueError("Knowledge base must contain a list")

    return articles


def retrieve_articles(
    message_text: str,
    category: str | None = None,
    limit: int = 3,
    path: Path = KNOWLEDGE_BASE_PATH,
) -> list[dict]:
    """Find relevant articles using keyword matching."""

    if limit <= 0:
        return []

    articles = load_articles(path)
    matches = []

    for article in articles:
        score = 0

        for keyword in article.get("keywords", []):
            pattern = (
                r"(?<!\w)"
                + re.escape(keyword)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                message_text,
                flags=re.IGNORECASE,
            ):
                score += 1

        if score == 0:
            continue

        if category and article.get("category") == category:
            score += 2

        matches.append((score, article))

    matches.sort(key=lambda item: item[0], reverse=True)

    return [
        article
        for score, article in matches[:limit]
    ]
