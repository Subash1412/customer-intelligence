from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.database import get_db
from app.modules.rag.repository import (
    RagRepository,
)
from app.modules.rag.service import (
    RagService,
)
from app.rag.embeddings import (
    TitanEmbeddingProvider,
)

from app.modules.rag.schemas import (
    RagQueryRequest,
    RagQueryResponse,
)


router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


def get_rag_service(
    db: AsyncSession = Depends(
        get_db
    ),
):

    return RagService(
        repository=RagRepository(db),
        embedding_provider=(
            TitanEmbeddingProvider()
        ),
    )


@router.post(
    "/documents/upload"
)
async def upload_document(
    file: UploadFile = File(...),
    service: RagService = Depends(
        get_rag_service
    ),
):

    try:

        return await service.ingest_pdf(
            file
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.post(
    "/query",
    response_model=RagQueryResponse,
)
async def query_rag(
    request: RagQueryRequest,
    service: RagService = Depends(
        get_rag_service
    ),
):

    return await service.query(
        question=request.question,
        top_k=request.top_k,
        max_distance=request.max_distance,
    )