import pytest
from unittest.mock import MagicMock
from dataclasses import dataclass
from app.repositories.customer_repository import CustomerRepository
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError
from sqlalchemy import delete
from app.models.DAO.customer_dao import CustomerDAO

@dataclass
class MockCustomerDTO:
    name: str
    surname: str
    
    def model_dump(self, exclude_unset=False):
        """Simulates Pydantic's model_dump for the update method."""
        return {"name": self.name, "surname": self.surname}

@pytest.mark.asyncio
class TestCustomerRepository:

    async def test_create_customer_success(self, db_session):
        repo = CustomerRepository(db_session)
        data = MockCustomerDTO(name="Bruce", surname="Wayne")
        
        customer = await repo.create_customer(data)
        
        assert customer.id is not None
        assert customer.name == "Bruce"
        assert customer.surname == "Wayne"

    async def test_create_customer_conflict(self, db_session):
        repo = CustomerRepository(db_session)
        data = MockCustomerDTO(name="Clark", surname="Kent")
        
        await repo.create_customer(data)
        
        with pytest.raises(ConflictError) as exc:
            await repo.create_customer(data)
        assert "already exists" in str(exc.value)

    async def test_get_customer_by_id_found(self, db_session):
        repo = CustomerRepository(db_session)
        created = await repo.create_customer(MockCustomerDTO("Diana", "Prince"))
        
        fetched = await repo.get_customer_by_id(created.id)
        assert fetched.name == "Diana"
        assert fetched.id == created.id

    async def test_get_customer_by_id_not_found(self, db_session):
        repo = CustomerRepository(db_session)
        with pytest.raises(NotFoundError):
            await repo.get_customer_by_id(999)

    async def test_search_customers_ilike(self, db_session):
        repo = CustomerRepository(db_session)
        await repo.create_customer(MockCustomerDTO("Arthur", "Curry"))
        await repo.create_customer(MockCustomerDTO("Barry", "Allen"))
        
        results = await repo.search_customers(name="ART")
        assert len(results) == 1
        assert results[0].name == "Arthur"

    async def test_update_customer_success(self, db_session):
        repo = CustomerRepository(db_session)
        customer = await repo.create_customer(MockCustomerDTO("Hal", "Jordan"))
        
        update_data = MagicMock()
        update_data.model_dump.return_value = {"surname": "Updated"}
        
        updated = await repo.update_customer(customer.id, update_data)
        
        assert updated.surname == "Updated"
        assert updated.name == "Hal"

    async def test_delete_customer_success(self, db_session):
        repo = CustomerRepository(db_session)
        customer = await repo.create_customer(MockCustomerDTO("Victor", "Stone"))
        
        await repo.delete_customer(customer.id)
        
        with pytest.raises(NotFoundError):
            await repo.get_customer_by_id(customer.id)

    async def test_list_customers(self, db_session):
        repo = CustomerRepository(db_session)
        
        await db_session.execute(delete(CustomerDAO))
        await db_session.commit()
        
        await repo.create_customer(MockCustomerDTO("User1", "Test"))
        await repo.create_customer(MockCustomerDTO("User2", "Test"))
        
        customers = await repo.list_customers()
        assert len(customers) == 2