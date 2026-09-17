from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class CustomerIntelligence(Base):

    __tablename__ = (
        "customer_intelligence"
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "customers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    sentiment: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    sentiment_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    intent: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    churn_risk: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    urgency: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    primary_issue: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    recommended_action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    model_provider: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )