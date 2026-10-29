
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TicketCategory(str, Enum):
    PAYMENT_ISSUE = "payment_issue"
    ORDER_STATUS = "order_status"
    DELIVERY_ISSUE = "delivery_issue"
    RETURN_REFUND = "return_refund"
    ACCOUNT_ACCESS = "account_access"
    PRODUCT_QUESTION = "product_question"
    COMPLAINT = "complaint"
    OTHER = "other"


class TicketPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ClassificationResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    category: TicketCategory
    priority: TicketPriority
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1, max_length=500)
    missing_information: list[str] = Field(default_factory=list)
    knowledge_article_ids: list[int] = Field(default_factory=list)
    draft_reply: str = Field(min_length=1, max_length=4000)
    requires_human_review: bool
