from app.modules.customers.repository import CustomerRepository
from app.modules.customers.schemas import (
    CustomerCreate,
    CustomerUpdate,
)


class CustomerService:

    def __init__(
        self,
        repository: CustomerRepository,
    ):
        self.repository = repository

    async def create_customer(
        self,
        data: CustomerCreate,
    ):

        existing = await self.repository.get_by_email(
            str(data.email)
        )

        if existing:
            raise ValueError(
                "Customer email already exists"
            )

        return await self.repository.create(data)

    async def get_customers(self):
        return await self.repository.get_all()

    async def get_customer(
        self,
        customer_id: int,
    ):
        return await self.repository.get_by_id(
            customer_id
        )

    async def update_customer(
        self,
        customer_id: int,
        data: CustomerUpdate,
    ):

        customer = await self.repository.get_by_id(
            customer_id
        )

        if not customer:
            return None

        return await self.repository.update(
            customer,
            data,
        )

    async def delete_customer(
        self,
        customer_id: int,
    ) -> bool:

        customer = await self.repository.get_by_id(
            customer_id
        )

        if not customer:
            return False

        await self.repository.delete(customer)

        return True