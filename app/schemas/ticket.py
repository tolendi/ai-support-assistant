
from pydantic import BaseModel, Field, ConfigDict


class TicketCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    message_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    message_text: str = Field(min_length=1, max_length=4000)
