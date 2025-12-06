from typing import List, Optional
from app.repositories.customer_repository import CustomerRepository
from app.repositories.loyalty_card_repository import LoyaltyCardRepository
from app.models.DTO.customer_dto import (
    CustomerCreateDTO,
    CustomerUpdateDTO,
    CustomerResponseDTO
)


class CustomerController:
    def __init__(self):
        self.customer_repo = CustomerRepository()
        self.loyalty_card_repo = LoyaltyCardRepository()

    async def create_customer(self, customer_dto: CustomerCreateDTO) -> CustomerResponseDTO:
        created_dao = await self.customer_repo.create_customer(customer_dto)
        return CustomerResponseDTO.model_validate(created_dao)

    async def get_customer_by_id(self, customer_id: int) -> CustomerResponseDTO:
        dao = await self.customer_repo.get_customer_by_id(customer_id)
        return CustomerResponseDTO.model_validate(dao)

    async def list_customers(self) -> List[CustomerResponseDTO]:
        daos = await self.customer_repo.list_customers()
        return [CustomerResponseDTO.model_validate(dao) for dao in daos]

    async def search_customers(
        self,
        name: Optional[str] = None,
        surname: Optional[str] = None
    ) -> List[CustomerResponseDTO]:
        daos = await self.customer_repo.search_customers(name=name, surname=surname)
        return [CustomerResponseDTO.model_validate(dao) for dao in daos]

    async def update_customer(
        self,
        customer_id: int,
        customer_dto: CustomerUpdateDTO
    ) -> CustomerResponseDTO:
        updated_dao = await self.customer_repo.update_customer(customer_id, customer_dto)
        return CustomerResponseDTO.model_validate(updated_dao)

    async def delete_customer(self, customer_id: int) -> None:
        await self.customer_repo.delete_customer(customer_id)

    async def attach_loyalty_card_to_customer(
        self,
        customer_id: int,
        card_id: int
    ) -> CustomerResponseDTO:
        # Verify customer exists
        await self.customer_repo.get_customer_by_id(customer_id)
        
        # Attach card to customer (updates customer_id on card)
        await self.loyalty_card_repo.attach_loyalty_card_to_customer(card_id, customer_id)
        
        # Return updated customer with attached card
        return await self.get_customer_by_id(customer_id)

