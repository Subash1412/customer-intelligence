import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]

ENVIRONMENT = os.getenv("APP_ENV", "development")

ENV_FILE = BASE_DIR / f".env.{ENVIRONMENT}"


class Settings(BaseSettings):
    APP_NAME: str = "Agentic AI Backend"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # AWS Bedrock
    LLM_PROVIDER: str = "bedrock"

    AWS_BEARER_TOKEN_BEDROCK: str

    AWS_REGION: str = "us-east-1"

    BEDROCK_MODEL_ID: str = (
    "us.amazon.nova-2-lite-v1:0"
    )

    BEDROCK_EMBEDDING_MODEL_ID: str = (
    "amazon.titan-embed-text-v2:0"
    )

    EMBEDDING_DIMENSIONS: int = 1024

    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()