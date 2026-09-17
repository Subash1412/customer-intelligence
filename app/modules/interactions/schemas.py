from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Channel = Literal[
    "whatsapp",
    "email",
    "call",
    "sms",
    "web",
]

Direction = Literal[
    "inbound",
    "outbound",
]

InteractionType = Literal[
    "enquiry",
    "complaint",
    "support",
    "purchase",
    "follow_up",
    "feedback",
    "other",
]


class InteractionCreate(BaseModel):
    customer_id: int

    channel: Channel
    direction: Direction
    interaction_type: InteractionType

    content: str = Field(
        min_length=1,
        max_length=10000,
    )

    occurred_at: datetime | None = None


class InteractionResponse(BaseModel):
    id: int
    customer_id: int

    channel: str
    direction: str
    interaction_type: str

    content: str

    occurred_at: datetime
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )