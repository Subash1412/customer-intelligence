from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.ai.schemas.customer_intelligence import (
    CustomerIntelligenceResult,
)
from app.modules.intelligence.models import (
    CustomerIntelligence,
)


class CustomerIntelligenceRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_by_customer(
        self,
        customer_id: int,
    ) -> CustomerIntelligence | None:

        statement = (
            select(CustomerIntelligence)
            .where(
                CustomerIntelligence.customer_id
                == customer_id
            )
        )

        result = await self.db.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def save(
        self,
        customer_id: int,
        result: CustomerIntelligenceResult,
        provider: str,
        model_name: str,
    ) -> CustomerIntelligence:

        intelligence = (
            await self.get_by_customer(
                customer_id
            )
        )

        values = result.model_dump()

        if intelligence:

            for field, value in values.items():
                setattr(
                    intelligence,
                    field,
                    value,
                )

            intelligence.model_provider = (
                provider
            )

            intelligence.model_name = (
                model_name
            )

        else:

            intelligence = (
                CustomerIntelligence(
                    customer_id=customer_id,
                    **values,
                    model_provider=provider,
                    model_name=model_name,
                )
            )

            self.db.add(
                intelligence
            )

        await self.db.commit()

        await self.db.refresh(
            intelligence
        )

        return intelligence