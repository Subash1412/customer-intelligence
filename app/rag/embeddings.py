import asyncio
import json
import os

import boto3

from app.core.config import settings


class TitanEmbeddingProvider:

    def __init__(self):

        os.environ[
            "AWS_BEARER_TOKEN_BEDROCK"
        ] = (
            settings
            .AWS_BEARER_TOKEN_BEDROCK
        )

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
        )

        self.model_id = (
            settings
            .BEDROCK_EMBEDDING_MODEL_ID
        )

    def _embed_sync(
        self,
        text: str,
    ) -> list[float]:

        body = {
            "inputText": text,
            "dimensions": (
                settings
                .EMBEDDING_DIMENSIONS
            ),
            "normalize": True,
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
        )

        result = json.loads(
            response["body"].read()
        )

        return result["embedding"]

    async def embed(
        self,
        text: str,
    ) -> list[float]:

        return await asyncio.to_thread(
            self._embed_sync,
            text,
        )