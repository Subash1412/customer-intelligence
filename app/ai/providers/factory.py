from app.ai.providers.base import LLMProvider
from app.ai.providers.bedrock_provider import (
    BedrockProvider,
)
from app.core.config import settings


def get_llm_provider() -> LLMProvider:

    provider = (
        settings.LLM_PROVIDER
        .strip()
        .lower()
    )

    if provider == "bedrock":
        return BedrockProvider()

    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )