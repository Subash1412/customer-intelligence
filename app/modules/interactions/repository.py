from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.interactions.models import Interaction
from app.modules.interactions.schemas import InteractionCreate


class InteractionRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        data: InteractionCreate,
    ) -> Interaction:

        values = data.model_dump(
            exclude={"occurred_at"}
        )

        interaction = Interaction(
            **values
        )

        if data.occurred_at is not None:
            interaction.occurred_at = data.occurred_at

        self.db.add(interaction)

        await self.db.commit()
        await self.db.refresh(interaction)

        return interaction

    async def get_by_id(
        self,
        interaction_id: int,
    ) -> Interaction | None:

        return await self.db.get(
            Interaction,
            interaction_id,
        )

    async def get_by_customer(
        self,
        customer_id: int,
    ) -> list[Interaction]:

        statement = (
            select(Interaction)
            .where(
                Interaction.customer_id
                == customer_id
            )
            .order_by(
                Interaction.occurred_at.desc()
            )
        )

        result = await self.db.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def delete(
        self,
        interaction: Interaction,
    ) -> None:

        await self.db.delete(
            interaction
        )

        await self.db.commit()