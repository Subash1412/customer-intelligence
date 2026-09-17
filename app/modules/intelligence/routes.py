from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.ai.providers.factory import (
    get_llm_provider,
)
from app.db.database import get_db

from app.modules.customers.repository import (
    CustomerRepository,
)
from app.modules.interactions.repository import (
    InteractionRepository,
)
from app.modules.intelligence.repository import (
    CustomerIntelligenceRepository,
)
from app.modules.intelligence.schemas import (
    CustomerIntelligenceResponse,
)
from app.modules.intelligence.service import (
    CustomerIntelligenceService,
)

from app.core.exceptions import (
    CustomerNotFoundError,
    NoInteractionsError,
)

router = APIRouter(
    tags=["Customer Intelligence"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
) -> CustomerIntelligenceService:

    return CustomerIntelligenceService(
        customer_repository=(
            CustomerRepository(db)
        ),
        interaction_repository=(
            InteractionRepository(db)
        ),
        intelligence_repository=(
            CustomerIntelligenceRepository(
                db
            )
        ),
        llm_provider=(
            get_llm_provider()
        ),
    )


@router.post(
    "/customers/{customer_id}/analyze",
    response_model=CustomerIntelligenceResponse,
)
async def analyze_customer(
    customer_id: int,
    service: CustomerIntelligenceService
        = Depends(get_service),
):
    try:
        return await service.analyze_customer(
            customer_id
        )

    except CustomerNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except NoInteractionsError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        )
@router.get(
    "/customers/{customer_id}/intelligence",
    response_model=CustomerIntelligenceResponse,
)
async def get_customer_intelligence(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
):

    repository = (
        CustomerIntelligenceRepository(
            db
        )
    )

    intelligence = (
        await repository.get_by_customer(
            customer_id
        )
    )

    if not intelligence:
        raise HTTPException(
            status_code=404,
            detail=(
                "Customer intelligence "
                "not generated yet"
            ),
        )

    return intelligence