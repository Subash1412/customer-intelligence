from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from app.modules.customers.repository import (
    CustomerRepository,
)

from app.modules.interactions.repository import (
    InteractionRepository,
)

from app.modules.interactions.schemas import (
    InteractionCreate,
    InteractionResponse,
)

from app.modules.interactions.service import (
    InteractionService,
)


router = APIRouter(
    tags=["Interactions"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
) -> InteractionService:

    interaction_repository = (
        InteractionRepository(db)
    )

    customer_repository = (
        CustomerRepository(db)
    )

    return InteractionService(
        interaction_repository,
        customer_repository,
    )


@router.post(
    "/interactions",
    response_model=InteractionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_interaction(
    data: InteractionCreate,
    service: InteractionService = Depends(
        get_service
    ),
):
    try:
        return await service.create_interaction(
            data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.get(
    "/customers/{customer_id}/interactions",
    response_model=list[InteractionResponse],
)
async def get_customer_interactions(
    customer_id: int,
    service: InteractionService = Depends(
        get_service
    ),
):
    try:
        return (
            await service.get_customer_interactions(
                customer_id
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.get(
    "/interactions/{interaction_id}",
    response_model=InteractionResponse,
)
async def get_interaction(
    interaction_id: int,
    service: InteractionService = Depends(
        get_service
    ),
):
    interaction = await service.get_interaction(
        interaction_id
    )

    if not interaction:
        raise HTTPException(
            status_code=404,
            detail="Interaction not found",
        )

    return interaction


@router.delete(
    "/interactions/{interaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_interaction(
    interaction_id: int,
    service: InteractionService = Depends(
        get_service
    ),
):
    deleted = await service.delete_interaction(
        interaction_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Interaction not found",
        )