import pytest
import uuid
from dataclasses import dataclass
from typing import Optional
from app.repositories.loyalty_card_repository import LoyaltyCardRepository
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError
from sqlalchemy import text

@dataclass
class MockLoyaltyCardDTO:
    card_code: str
    customer_id: Optional[int] = None
    points: int = 0

@pytest.mark.asyncio
class TestLoyaltyCardRepository:

    async def create_unique_customer(self, db_session):
        """Helper to create a fresh customer for every card to satisfy UNIQUE constraints."""
        unique_suffix = uuid.uuid4().hex[:6]
        await db_session.execute(text(
            f"INSERT INTO customers (name, surname) VALUES ('User_{unique_suffix}', 'Test')"
        ))
        await db_session.commit()
        result = await db_session.execute(text("SELECT id FROM customers ORDER BY id DESC LIMIT 1"))
        return result.scalar()

    async def test_create_loyalty_card_success(self, db_session):
        repo = LoyaltyCardRepository(db_session)
        customer_id = await self.create_unique_customer(db_session)
        
        data = MockLoyaltyCardDTO(card_code=f"CARD-{uuid.uuid4().hex[:4]}", customer_id=customer_id, points=100)
        card = await repo.create_loyalty_card(data)
        
        assert card.id is not None
        assert card.customer_id == customer_id

    async def test_create_loyalty_card_conflict(self, db_session):
        repo = LoyaltyCardRepository(db_session)
        customer_id = await self.create_unique_customer(db_session)
        code = "UNIQUE-CODE-123"
        
        await repo.create_loyalty_card(MockLoyaltyCardDTO(card_code=code, customer_id=customer_id))
        
        other_customer = await self.create_unique_customer(db_session)
        with pytest.raises(ConflictError):
            await repo.create_loyalty_card(MockLoyaltyCardDTO(card_code=code, customer_id=other_customer))

    async def test_add_points_success(self, db_session):
        repo = LoyaltyCardRepository(db_session)
        customer_id = await self.create_unique_customer(db_session)
        card = await repo.create_loyalty_card(
            MockLoyaltyCardDTO(card_code=f"P-{uuid.uuid4().hex[:4]}", customer_id=customer_id, points=50)
        )
        
        updated_card = await repo.add_points(card.id, 25)
        assert updated_card.points == 75

    async def test_attach_loyalty_card_to_customer(self, db_session):
        repo = LoyaltyCardRepository(db_session)
        
        card = await repo.create_loyalty_card(MockLoyaltyCardDTO(card_code=f"ATTACH-{uuid.uuid4().hex[:4]}"))
        
        customer_id = await self.create_unique_customer(db_session)

        updated_card = await repo.attach_loyalty_card_to_customer(card.id, customer_id)
        assert updated_card.customer_id == customer_id

    async def test_attach_duplicate_customer_fails(self, db_session):
        """Test that attaching a card to a customer who already has one fails (due to DB constraint)."""
        repo = LoyaltyCardRepository(db_session)
        
        c1_id = await self.create_unique_customer(db_session)
        await repo.create_loyalty_card(MockLoyaltyCardDTO(card_code="CARD-A", customer_id=c1_id))
        
        card_b = await repo.create_loyalty_card(MockLoyaltyCardDTO(card_code="CARD-B"))
        
        with pytest.raises(Exception): 
            await repo.attach_loyalty_card_to_customer(card_b.id, c1_id)