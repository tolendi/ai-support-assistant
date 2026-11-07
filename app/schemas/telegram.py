from pydantic import BaseModel, ConfigDict


class TelegramWebhookRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    update_id: int
    message: dict | None = None