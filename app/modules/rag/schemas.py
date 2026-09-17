from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=2000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    max_distance: float = Field(
        default=0.75,
        ge=0.0,
        le=2.0,
    )


class RagSource(BaseModel):
    document_id: int
    filename: str
    page_number: int | None
    chunk_index: int
    distance: float


class RagQueryResponse(BaseModel):
    answer: str
    sources: list[RagSource]