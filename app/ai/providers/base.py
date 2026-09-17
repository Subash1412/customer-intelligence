from abc import ABC, abstractmethod

from app.ai.schemas.customer_intelligence import (
    CustomerIntelligenceResult,
)


class LLMProvider(ABC):

    @abstractmethod
    async def analyze_customer(
        self,
        system_prompt: str,
        user_prompt: str,
        # customer_context: str,
    ) -> CustomerIntelligenceResult:
        pass