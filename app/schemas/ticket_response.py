from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message_id: int
    user_id: int
    message_text: str
    category: str
    priority: str
    confidence: float
    reason: str
    draft_reply: str
    requires_human_review: bool
    status: str
    created_at: datetime