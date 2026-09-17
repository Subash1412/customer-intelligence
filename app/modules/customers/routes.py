from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.modules.customers.repository import CustomerRepository
from app.modules.customers.schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
)
from app.modules.customers.service import CustomerService


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
) -> CustomerService:

    repository = CustomerRepository(db)

    return CustomerService(repository)


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    data: CustomerCreate,
    service: CustomerService = Depends(get_service),
):
    try:
        return await service.create_customer(data)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get(
    "",
    response_model=list[CustomerResponse],
)
async def get_customers(
    service: CustomerService = Depends(get_service),
):
    return await service.get_customers()


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
)
async def get_customer(
    customer_id: int,
    service: CustomerService = Depends(get_service),
):
    customer = await service.get_customer(
        customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer


@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
)
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    service: CustomerService = Depends(get_service),
):
    customer = await service.update_customer(
        customer_id,
        data,
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_customer(
    customer_id: int,
    service: CustomerService = Depends(get_service),
):
    deleted = await service.delete_customer(
        customer_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )