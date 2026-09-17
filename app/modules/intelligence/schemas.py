from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class CustomerIntelligenceResponse(
    BaseModel
):
    id: int
    customer_id: int

    sentiment: str
    sentiment_score: float

    intent: str
    churn_risk: str
    urgency: str

    primary_issue: str | None

    summary: str
    recommended_action: str

    model_provider: str
    model_name: str

    analyzed_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )