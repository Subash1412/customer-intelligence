from app.ai.providers.base import (
    LLMProvider,
)
from app.core.config import settings

from app.modules.customers.repository import (
    CustomerRepository,
)
from app.modules.interactions.repository import (
    InteractionRepository,
)
from app.modules.intelligence.repository import (
    CustomerIntelligenceRepository,
)

from app.core.exceptions import (
    CustomerNotFoundError,
    NoInteractionsError,
)


class CustomerIntelligenceService:

    def __init__(
        self,
        customer_repository:
            CustomerRepository,

        interaction_repository:
            InteractionRepository,

        intelligence_repository:
            CustomerIntelligenceRepository,

        llm_provider:
            LLMProvider,
    ):
        self.customers = (
            customer_repository
        )

        self.interactions = (
            interaction_repository
        )

        self.intelligence = (
            intelligence_repository
        )

        self.llm = llm_provider

    async def analyze_customer(
        self,
        customer_id: int,
    ):

        customer = (
            await self.customers.get_by_id(
                customer_id
            )
        )

        if not customer:
            raise CustomerNotFoundError(
             "Customer not found"
        )

        interactions = (
            await self.interactions
            .get_by_customer(
                customer_id
            )
        )

        if not interactions:
            raise NoInteractionsError(
                "Customer has no interactions"
            )

        chronological = list(
            reversed(interactions)
        )

        interaction_text = "\n".join(
            (
                f"{item.occurred_at} | "
                f"{item.direction} | "
                f"{item.channel} | "
                f"{item.interaction_type} | "
                f"{item.content}"
            )
            for item in chronological
        )

        customer_context = f"""
CUSTOMER

Name: {customer.name}
Company: {customer.company or "Unknown"}
Status: {customer.status}

INTERACTION HISTORY

{interaction_text}
"""

        result = (
            await self.llm
            .analyze_customer(
                customer_context
            )
        )

        return (
            await self.intelligence.save(
                customer_id=customer_id,
                result=result,
                provider=(
                    settings.LLM_PROVIDER
                ),
                model_name=(
                    settings.BEDROCK_MODEL_ID
                ),
            )
        )