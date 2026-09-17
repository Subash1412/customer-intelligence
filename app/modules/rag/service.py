import hashlib
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.modules.rag.repository import RagRepository
from app.rag.chunker import chunk_text
from app.rag.embeddings import TitanEmbeddingProvider
from app.rag.generator import RagGenerator
from app.rag.pdf_reader import read_pdf
from app.rag.retriever import RagRetriever


STORAGE_DIR = Path(
    "storage/documents"
)


class RagService:

    def __init__(
        self,
        repository: RagRepository,
        embedding_provider: TitanEmbeddingProvider,
    ):
        self.repository = repository
        self.embedding_provider = embedding_provider

    async def ingest_pdf(
        self,
        file: UploadFile,
    ):
        if file.content_type != "application/pdf":
            raise ValueError(
                "Only PDF files are supported"
            )

        file_bytes = await file.read()

        file_hash = hashlib.sha256(
            file_bytes
        ).hexdigest()

        existing = (
            await self.repository
            .get_document_by_hash(
                file_hash
            )
        )

        try:
            document = (
            await self.repository
            .create_document(
            filename=file.filename,
            content_type=file.content_type,
            file_hash=file_hash,
            storage_path=str(file_path),
            )
        )

        except IntegrityError:
            if file_path.exists():
                file_path.unlink()

        raise ValueError(
            "Document already uploaded"
        )

        if existing:
            raise ValueError(
                "Document already uploaded"
            )

        STORAGE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        safe_filename = (
            f"{uuid4()}_{file.filename}"
        )

        file_path = (
            STORAGE_DIR / safe_filename
        )

        file_path.write_bytes(
            file_bytes
        )

        document = (
            await self.repository
            .create_document(
                filename=file.filename,
                content_type=file.content_type,
                file_hash=file_hash,
                storage_path=str(
                    file_path
                ),
            )
        )

        pages = read_pdf(
            file_path
        )

        full_text = "\n".join(
            page["text"]
            for page in pages
        )

        normalized_text = " ".join(
            full_text.lower().split()
        )

        content_hash = hashlib.sha256(
            normalized_text.encode("utf-8")
        ).hexdigest()

        chunk_index = 0

        for page in pages:

            chunks = chunk_text(
                text=page["text"],
                page_number=(
                    page["page_number"]
                ),
            )

            for chunk in chunks:

                embedding = (
                    await self.embedding_provider
                    .embed(
                        chunk["content"]
                    )
                )

                await self.repository.create_chunk(
                    document_id=document.id,
                    chunk_index=chunk_index,
                    content=chunk["content"],
                    page_number=(
                        chunk["page_number"]
                    ),
                    embedding=embedding,
                )

                chunk_index += 1

        document = (
            await self.repository
            .mark_complete(
                document
            )
        )

        return {
            "document_id": document.id,
            "filename": document.filename,
            "status": document.status,
            "chunks_created": chunk_index,
        }
    async def query(
        self,
        question: str,
        top_k: int = 5,
        max_distance: float = 0.75,
        ):
            retriever = RagRetriever(
            repository=self.repository,
            embedding_provider=self.embedding_provider,
          )

            results = await retriever.retrieve(
                query=question,
                top_k=top_k,
                max_distance=max_distance,
            )

            if not results:
                return {
                    "answer": (
                        "The uploaded documents do not contain "
                        "sufficient relevant information to answer this question."
                    ),
                    "sources": [],
                }

            context_parts = []
            sources = []

            for (
                chunk,
                document,
                distance,
            ) in results:

                context_parts.append(
                    f"""
    SOURCE:
    {document.filename}

    PAGE:
    {chunk.page_number}

    CONTENT:
    {chunk.content}
    """
                )

                sources.append(
                    {
                        "document_id":
                            document.id,

                        "filename":
                            document.filename,

                        "page_number":
                            chunk.page_number,

                        "chunk_index":
                            chunk.chunk_index,

                        "distance":
                            float(distance),
                    }
                )

            context = "\n\n".join(
                context_parts
            )

            generator = RagGenerator()

            answer = await generator.generate(
                question=question,
                context=context,
            )

            return {
                "answer": answer,
                "sources": sources,
            }

    def create_retriever(
    self,
) -> RagRetriever:

        return RagRetriever(
            repository=self.repository,
            embedding_provider=(
                self.embedding_provider
            ),
        )

        async def retrieve_policy(
        self,
        state: AgentState,
        ) -> dict:

            retriever = (
                self.rag.create_retriever()
            )

            results = await retriever.retrieve(
                query=state["question"],
                top_k=3,
                max_distance=0.75,
            )

            contexts = []

            for (
                chunk,
                document,
                distance,
            ) in results:

                contexts.append(
                    f"""
        SOURCE:
        {document.filename}

        PAGE:
        {chunk.page_number}

        CONTENT:
        {chunk.content}
        """
                )

            return {
                "policy_context":
                    "\n\n".join(contexts)
            }