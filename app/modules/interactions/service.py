from app.modules.customers.repository import CustomerRepository
from app.modules.interactions.repository import InteractionRepository
from app.modules.interactions.schemas import InteractionCreate


class InteractionService:

    def __init__(
        self,
        interaction_repository: InteractionRepository,
        customer_repository: CustomerRepository,
    ):
        self.interactions = interaction_repository
        self.customers = customer_repository

    async def create_interaction(
        self,
        data: InteractionCreate,
    ):
        customer = await self.customers.get_by_id(
            data.customer_id
        )

        if not customer:
            raise ValueError(
                "Customer not found"
            )

        return await self.interactions.create(
            data
        )

    async def get_customer_interactions(
        self,
        customer_id: int,
    ):
        customer = await self.customers.get_by_id(
            customer_id
        )

        if not customer:
            raise ValueError(
                "Customer not found"
            )

        return await self.interactions.get_by_customer(
            customer_id
        )

    async def get_interaction(
        self,
        interaction_id: int,
    ):
        return await self.interactions.get_by_id(
            interaction_id
        )

    async def delete_interaction(
        self,
        interaction_id: int,
    ) -> bool:

        interaction = await self.interactions.get_by_id(
            interaction_id
        )

        if not interaction:
            return False

        await self.interactions.delete(
            interaction
        )

        return True