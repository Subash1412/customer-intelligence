import os

import boto3

from app.core.config import settings


def test_bedrock():

    # Make the Bedrock API key visible to Boto3
    os.environ[
        "AWS_BEARER_TOKEN_BEDROCK"
    ] = settings.AWS_BEARER_TOKEN_BEDROCK

    client = boto3.client(
        service_name="bedrock-runtime",
        region_name=settings.AWS_REGION,
    )

    response = client.converse(
        modelId=settings.BEDROCK_MODEL_ID,

        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": (
                            "Reply with exactly: "
                            "Bedrock connection successful"
                        )
                    }
                ],
            }
        ],

        inferenceConfig={
            "maxTokens": 50,
            "temperature": 0,
        },
    )

    text = response[
        "output"
    ][
        "message"
    ][
        "content"
    ][0][
        "text"
    ]

    print(text)


if __name__ == "__main__":
    test_bedrock()