
import pytest
from pydantic import ValidationError

from app.schemas.classification import ClassificationResult


def valid_classification_data():
    return {
        "category": "payment_issue",
        "priority": "high",
        "confidence": 0.91,
        "reason": "Possible duplicate payment",
        "missing_information": ["order_id"],
        "knowledge_article_ids": [12],
        "draft_reply": "Please provide your order ID.",
        "requires_human_review": True,
    }


def test_valid_classification():
    result = ClassificationResult(**valid_classification_data())

    assert result.category == "payment_issue"
    assert result.priority == "high"
    assert result.confidence == 0.91


def test_invalid_category():
    data = valid_classification_data()
    data["category"] = "something_unknown"

    with pytest.raises(ValidationError):
        ClassificationResult(**data)


def test_confidence_out_of_range():
    data = valid_classification_data()
    data["confidence"] = 1.5

    with pytest.raises(ValidationError):
        ClassificationResult(**data)


def test_empty_reason():
    data = valid_classification_data()
    data["reason"] = "   "

    with pytest.raises(ValidationError):
        ClassificationResult(**data)


def test_unknown_field_is_rejected():
    data = valid_classification_data()
    data["unexpected_field"] = "value"

    with pytest.raises(ValidationError):
        ClassificationResult(**data)
