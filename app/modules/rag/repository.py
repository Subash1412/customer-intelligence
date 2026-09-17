from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.rag.models import (
    RagChunk,
    RagDocument,
)


class RagRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_document_by_hash(
        self,
        file_hash: str,
    ) -> RagDocument | None:

        result = await self.db.execute(
            select(RagDocument)
            .where(
                RagDocument.file_hash
                == file_hash
            )
        )

        return result.scalar_one_or_none()

    async def create_document(
    self,
    filename: str,
    content_type: str,
    file_hash: str,
    storage_path: str,
    ) -> RagDocument:

        document = RagDocument(
            filename=filename,
            content_type=content_type,
            file_hash=file_hash,
            storage_path=storage_path,
            status="processing",
        )

        self.db.add(document)

        try:
            await self.db.flush()

        except IntegrityError:
            await self.db.rollback()
            raise

        return document

        document = RagDocument(
            filename=filename,
            content_type=content_type,
            file_hash=file_hash,
            storage_path=storage_path,
            status="processing",
        )

        self.db.add(document)

        await self.db.flush()

        return document

    async def create_chunk(
        self,
        document_id: int,
        chunk_index: int,
        content: str,
        page_number: int | None,
        embedding: list[float],
    ) -> RagChunk:

        chunk = RagChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            page_number=page_number,
            embedding=embedding,
        )

        self.db.add(chunk)

        return chunk

    async def mark_complete(
        self,
        document: RagDocument,
    ):

        document.status = "completed"

        await self.db.commit()

        await self.db.refresh(
            document
        )

        return document
    async def search_chunks(
    self,
    query_embedding: list[float],
    limit: int = 5,
    ):

        statement = (
        select(
            RagChunk,
            RagChunk.embedding
            .cosine_distance(
                query_embedding
            )
            .label("distance"),
        )
        .order_by(
            RagChunk.embedding
            .cosine_distance(
                query_embedding
            )
        )
        .limit(limit)
    )

        result = await self.db.execute(
            statement
        )

        return result.all()

    async def search_chunks(
    self,
    query_embedding: list[float],
    limit: int = 5,
    max_distance: float = 0.75,
    ):
        distance = (
            RagChunk.embedding
            .cosine_distance(
                query_embedding
            )
        )

        statement = (
            select(
                RagChunk,
                RagDocument,
                distance.label("distance"),
            )
            .join(
                RagDocument,
                RagChunk.document_id
                == RagDocument.id,
            )
            .where(
                RagDocument.status == "completed"
            )
            .where(
                distance <= max_distance
            )
            .order_by(
                distance
            )
            .limit(limit)
        )

        result = await self.db.execute(
            statement
        )

        return result.all()


async def get_document_by_content_hash(
    self,
    content_hash: str,
) -> RagDocument | None:

    result = await self.db.execute(
        select(RagDocument)
        .where(
            RagDocument.content_hash
            == content_hash
        )
    )

    return result.scalar_one_or_none()



#         existing_content = (
#     await self.repository
#     .get_document_by_content_hash(
#         content_hash
#     )
# )

# if existing_content:
#     file_path.unlink(
#         missing_ok=True
#     )

#     raise ValueError(
#         "A document with the same content "
#         "has already been uploaded"
#     )