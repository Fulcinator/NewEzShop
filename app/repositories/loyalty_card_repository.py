from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import AsyncSessionLocal
from app.models.DAO.loyaltyCard_dao import LoyaltyCardDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError


class LoyaltyCardRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self):
        return self._session or AsyncSessionLocal()

    async def create_loyalty_card(self, data) -> LoyaltyCardDAO:
        async with await self._get_session() as session:
            # Verify that card_code is unique
            result = await session.execute(
                select(LoyaltyCardDAO).where(
                    LoyaltyCardDAO.card_code == data.card_code
                )
            )
            existing = result.scalars().first() 
            if existing:
                raise ConflictError(f"Loyalty card with code {data.card_code} already exists")

            dao = LoyaltyCardDAO(
                card_code=data.card_code,
                points=data.points or 0,
                customer_id=data.customer_id
            )
            
            session.add(dao)
            await session.commit()
            await session.refresh(dao)
            
            return dao

    async def attach_loyalty_card_to_customer(
        self,
        loyalty_card_id: int,
        customer_id: int
    ) -> LoyaltyCardDAO:
        async with await self._get_session() as session:
            # Retrieve the card
            card = await session.get(LoyaltyCardDAO, loyalty_card_id)
            if not card:
                raise NotFoundError(f"Loyalty card with id {loyalty_card_id} not found")

            # Import here to avoid circular imports
            from app.models.DAO.customer_dao import CustomerDAO
            
            # Verify the customer exists
            customer = await session.get(CustomerDAO, customer_id)
            if not customer:
                raise NotFoundError(f"Customer with id {customer_id} not found")

            # Associate the card to the customer
            card.customer_id = customer_id
            
            await session.commit()
            await session.refresh(card)
            return card

    async def add_points(self, loyalty_card_id: int, points: int) -> LoyaltyCardDAO:
        async with await self._get_session() as session:
            card = await session.get(LoyaltyCardDAO, loyalty_card_id)
            
            if not card:
                raise NotFoundError(f"Loyalty card with id {loyalty_card_id} not found")
            card.points += points
            
            if card.points < 0:
                card.points = 0
            
            await session.commit()
            await session.refresh(card)
            return card
