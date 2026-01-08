from typing import List, Optional
from unittest import result
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
            # Verify that card_id is unique
            result = await session.execute(
                select(LoyaltyCardDAO).where(
                    LoyaltyCardDAO.card_id == data.card_id
                )
            )
            existing = result.scalars().first() 
            if existing:
                raise ConflictError(f"Loyalty card with id {data.card_id} already exists")

            dao = LoyaltyCardDAO(
                card_id=data.card_id,
                points=data.points or 0,
            )
            
            session.add(dao)
            await session.commit()
            await session.refresh(dao)
            
            return dao

    async def attach_loyalty_card_to_customer(
        self,
        loyalty_card_id: str,
        customer_id: int
    ) -> LoyaltyCardDAO:
        async with await self._get_session() as session:
            # Retrieve the card
            loyalty_card_id = str(loyalty_card_id).zfill(10)
            print(f"Attaching card {loyalty_card_id} to customer {customer_id}")
            result = await session.execute(
            select(LoyaltyCardDAO).where(LoyaltyCardDAO.card_id == loyalty_card_id)
            )
            card = result.scalars().first()

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

    async def add_points(self, loyalty_card_id: str, points: int) -> LoyaltyCardDAO:
        async with await self._get_session() as session:
            result = await session.execute(
            select(LoyaltyCardDAO).where(LoyaltyCardDAO.card_id == loyalty_card_id)
            )
            card = result.scalars().first()

            if not card:
                raise NotFoundError(f"Loyalty card with id {loyalty_card_id} not found")
            card.points += points
            
            if card.points < 0:
                card.points = 0
            
            await session.commit()
            await session.refresh(card)
            return card

    async def delete_card(self, card_id: str):
        async with await self._get_session() as session:
            result = await session.execute(
                select(LoyaltyCardDAO).where(LoyaltyCardDAO.card_id == card_id)
            )
            card = result.scalars().first()
            if card:
                await session.delete(card)
                await session.commit()

    async def update_card(self, old_card_id: str, new_card_id: str, points: int):
        async with await self._get_session() as session:
            result = await session.execute(
                select(LoyaltyCardDAO).where(LoyaltyCardDAO.card_id == old_card_id)
            )
            card = result.scalars().first()
            if not card:
                raise NotFoundError("Card not found")

            card.card_id = new_card_id
            card.points = points

            await session.commit()
            await session.refresh(card)
            return card

    async def create_loyalty_card_and_attach(self, customer_id: int, card_id: str, points: int):
        async with await self._get_session() as session:
            dao = LoyaltyCardDAO(
                card_id=card_id,
                points=points,
                customer_id=customer_id
            )
            session.add(dao)
            await session.commit()
            await session.refresh(dao)
            return dao