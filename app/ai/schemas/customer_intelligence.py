from typing import Literal

from pydantic import BaseModel, Field


class CustomerIntelligenceResult(BaseModel):

    sentiment: Literal[
        "positive",
        "neutral",
        "negative",
    ]

    sentiment_score: float = Field(
        ge=-1.0,
        le=1.0,
    )

    intent: Literal[
        "general_enquiry",
        "purchase_interest",
        "support_request",
        "complaint",
        "possible_cancellation",
        "feedback",
        "unknown",
    ]

    churn_risk: Literal[
        "low",
        "medium",
        "high",
    ]

    urgency: Literal[
        "low",
        "medium",
        "high",
    ]

    primary_issue: str | None = None

    summary: str

    recommended_action: str