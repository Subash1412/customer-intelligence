import asyncio
import json
import os

import boto3
from pydantic import ValidationError

from app.ai.prompts.customer_analysis import (
    CUSTOMER_ANALYSIS_SYSTEM_PROMPT,
)
from app.ai.providers.base import LLMProvider
from app.ai.schemas.customer_intelligence import (
    CustomerIntelligenceResult,
)
from app.core.config import settings


class BedrockProvider(LLMProvider):

    def __init__(self):

        os.environ[
            "AWS_BEARER_TOKEN_BEDROCK"
        ] = settings.AWS_BEARER_TOKEN_BEDROCK

        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.AWS_REGION,
        )

        self.model_id = (
            settings.BEDROCK_MODEL_ID
        )

    def _call_bedrock(
        self,
        customer_context: str,
    ) -> CustomerIntelligenceResult:

        response = self.client.converse(
            modelId=self.model_id,

            system=[
                {
                    "text":
                        CUSTOMER_ANALYSIS_SYSTEM_PROMPT
                }
            ],

            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": customer_context
                        }
                    ],
                }
            ],

            inferenceConfig={
                "maxTokens": 1000,
                "temperature": 0,
            },
        )

        content_blocks = (
            response
            .get("output", {})
            .get("message", {})
            .get("content", [])
        )

        text = next(
            (
                block["text"]
                for block in content_blocks
                if "text" in block
            ),
            None,
        )

        if not text:
            raise RuntimeError(
                "Bedrock returned no text content"
            )

        cleaned_text = text.strip()

        if cleaned_text.startswith("```json"):
            cleaned_text = (
                cleaned_text
                .removeprefix("```json")
                .removesuffix("```")
                .strip()
            )

        elif cleaned_text.startswith("```"):
            cleaned_text = (
                cleaned_text
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )

        try:
            raw_json = json.loads(
                cleaned_text
            )

        except json.JSONDecodeError as error:
            raise RuntimeError(
                "Bedrock returned invalid JSON. "
                f"Raw response: {text}"
            ) from error

        try:
            return (
                CustomerIntelligenceResult
                .model_validate(
                    raw_json
                )
            )

        except ValidationError as error:
            raise RuntimeError(
                "Bedrock JSON did not match "
                "CustomerIntelligenceResult schema. "
                f"Raw response: {raw_json}"
            ) from error

    async def analyze_customer(
        self,
        customer_context: str,
    ) -> CustomerIntelligenceResult:

        return await asyncio.to_thread(
            self._call_bedrock,
            customer_context,
        )

    def _generate_sync(
    self,
    system_prompt: str,
    user_prompt: str,
    ) -> str:

        response = self.client.converse(
            modelId=self.model_id,

            system=[
                {
                    "text":
                        system_prompt
                }
            ],

            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text":
                                user_prompt
                        }
                    ],
                }
            ],

            inferenceConfig={
                "temperature": 0,
                "maxTokens": 800,
            },
        )

        content_blocks = (
            response
            .get("output", {})
            .get("message", {})
            .get("content", [])
        )

        text = next(
            (
                block["text"]
                for block
                in content_blocks
                if "text" in block
            ),
            None,
        )

        if not text:
            raise RuntimeError(
                "Bedrock returned no text"
            )

        return text


    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        return await asyncio.to_thread(
            self._generate_sync,
            system_prompt,
            user_prompt,
        )


    async def converse_with_tools(
    self,
    messages: list,
    tool_config: dict,
):
        return await asyncio.to_thread(
            self._converse_with_tools_sync,
            messages,
            tool_config,
        )


    def _converse_with_tools_sync(
    self,
    messages: list,
    tool_config: dict,
):

        return self.client.converse(
            modelId=self.model_id,

            system=[
                {
                    "text": """
    You are a customer intelligence agent.

    Use available tools when information is
    required to answer the user's question.

    Do not invent customer information.
    Do not invent company policy.

    Use customer tools for customer-specific
    information.

    Use the policy search tool when company
    rules or policies are relevant.

    Base your final answer on tool results.
    """
                }
            ],

            messages=messages,

            toolConfig=tool_config,

            inferenceConfig={
                "temperature": 0,
                "maxTokens": 1000,
            },
        )