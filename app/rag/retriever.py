from app.modules.rag.repository import (
    RagRepository,
)
from app.rag.embeddings import (
    TitanEmbeddingProvider,
)

class RagRetriever:

    def __init__(
        self,
        repository: RagRepository,
        embedding_provider: TitanEmbeddingProvider,
    ):
        self.repository = repository
        self.embedding_provider = (
            embedding_provider
        )

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        max_distance: float = 0.75,
    ):
        query_embedding = (
            await self.embedding_provider
            .embed(query)
        )

        return (
            await self.repository.search_chunks(
                query_embedding=query_embedding,
                limit=top_k,
                max_distance=max_distance,
            )
        )