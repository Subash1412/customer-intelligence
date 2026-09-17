from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customers.models import Customer
from app.modules.customers.schemas import (
    CustomerCreate,
    CustomerUpdate,
)


class CustomerRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: CustomerCreate,
    ) -> Customer:

        customer = Customer(
            **data.model_dump()
        )

        self.db.add(customer)

        await self.db.commit()
        await self.db.refresh(customer)

        return customer

    async def get_all(self) -> list[Customer]:

        result = await self.db.execute(
            select(Customer)
        )

        return list(
            result.scalars().all()
        )

    async def get_by_id(
        self,
        customer_id: int,
    ) -> Customer | None:

        return await self.db.get(
            Customer,
            customer_id,
        )

    async def get_by_email(
        self,
        email: str,
    ) -> Customer | None:

        result = await self.db.execute(
            select(Customer).where(
                Customer.email == email
            )
        )

        return result.scalar_one_or_none()

    async def update(
        self,
        customer: Customer,
        data: CustomerUpdate,
    ) -> Customer:

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(customer, field, value)

        await self.db.commit()
        await self.db.refresh(customer)

        return customer

    async def delete(
        self,
        customer: Customer,
    ) -> None:

        await self.db.delete(customer)
        await self.db.commit()