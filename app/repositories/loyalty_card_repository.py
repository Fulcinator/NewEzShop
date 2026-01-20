from typing import List, Optional
from unittest import result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import AsyncSessionLocal
from app.models.DAO.loyaltyCard_dao import LoyaltyCardDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.general_error import GeneralError
import random


class LoyaltyCardRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self):
        return self._session or AsyncSessionLocal()

    async def _generate_unique_card_id(self, session: AsyncSession) -> str:
        while True:
            card_id = str(random.randint(1000000000, 9999999999))
            result = await session.execute(
                select(LoyaltyCardDAO).where(LoyaltyCardDAO.card_id == card_id)
            )
            if not result.scalars().first():
                return card_id

    async def create_loyalty_card(self, data) -> LoyaltyCardDAO:
        async with await self._get_session() as session:
            if data is None:
                card_id = await self._generate_unique_card_id(session)
                points = 0
            else:
                if data.card_id is None:
                    card_id = await self._generate_unique_card_id(session)
                else:
                    card_id = data.card_id
                    result = await session.execute(
                        select(LoyaltyCardDAO).where(
                            LoyaltyCardDAO.card_id == card_id
                        )
                    )
                    existing = result.scalars().first() 
                    if existing:
                        raise ConflictError(f"Loyalty card with id {card_id} already exists")
                
                points = data.points or 0

            dao = LoyaltyCardDAO(
                card_id=card_id,
                points=points,
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

            if card.customer_id is not None and card.customer_id != customer_id:
                raise ConflictError(f"Loyalty card {loyalty_card_id} is already attached to another customer")

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
            
            new_points = card.points + points
            if new_points < 0:
                raise GeneralError(f"Insufficient points. Card has {card.points} points, cannot remove {abs(points)} points")
            
            card.points = new_points
            
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