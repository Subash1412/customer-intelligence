import asyncio
import os

import boto3

from app.core.config import settings


RAG_SYSTEM_PROMPT = """
You answer questions using company policy documents.

Rules:

1. Use only the provided context.
2. Do not invent company policy.
3. If the answer is not present in the context,
   clearly say that the policy does not specify it.
4. Be concise and practical.
5. Do not claim a policy rule unless the supplied
   context supports it.
"""


class RagGenerator:

    def __init__(self):

        os.environ[
            "AWS_BEARER_TOKEN_BEDROCK"
        ] = settings.AWS_BEARER_TOKEN_BEDROCK

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
        )

    def _generate_sync(
        self,
        question: str,
        context: str,
    ) -> str:

        response = self.client.converse(
            modelId=(
                settings
                .BEDROCK_MODEL_ID
            ),

            system=[
                {
                    "text":
                        RAG_SYSTEM_PROMPT
                }
            ],

            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": f"""
CONTEXT

{context}

QUESTION

{question}
"""
                        }
                    ],
                }
            ],

            inferenceConfig={
                "temperature": 0,
                "maxTokens": 800,
            },
        )

        blocks = (
            response["output"]
            ["message"]
            ["content"]
        )

        for block in blocks:
            if "text" in block:
                return block["text"]

        raise RuntimeError(
            "Nova returned no text"
        )

    async def generate(
        self,
        question: str,
        context: str,
    ) -> str:

        return await asyncio.to_thread(
            self._generate_sync,
            question,
            context,
        )