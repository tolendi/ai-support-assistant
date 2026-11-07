from pydantic import BaseModel, ConfigDict

from app.schemas.classification import TicketStatus


class TicketStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: TicketStatus