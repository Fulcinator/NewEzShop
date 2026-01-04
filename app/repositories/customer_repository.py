from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database.database import AsyncSessionLocal
from app.models.DAO.customer_dao import CustomerDAO
from app.models.DAO.loyaltyCard_dao import LoyaltyCardDAO
from app.models.DTO.customer_dto import CustomerUpdateDTO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError


class CustomerRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self):
        return self._session or AsyncSessionLocal()

    async def create_customer(self, data) -> CustomerDAO:
        async with await self._get_session() as session:
            # Conflict checking
            result = await session.execute(
                select(CustomerDAO).where(
                    (CustomerDAO.name == data.name)
                )
            )
            existing = result.scalars().first()
            if existing:
                raise ConflictError("Customer with same name already exists")
            
            dao = CustomerDAO(
                name=data.name
            )
            
            session.add(dao)
            await session.commit()
            result = await session.execute(
                select(CustomerDAO)
                .where(CustomerDAO.id == dao.id)
                .options(selectinload(CustomerDAO.loyalty_card))
            )
            return result.scalars().first()

    async def get_customer_by_id(self, id: int) -> CustomerDAO:
        async with await self._get_session() as session:
            result = await session.execute(
                select(CustomerDAO)
                .where(CustomerDAO.id == id)
                .options(selectinload(CustomerDAO.loyalty_card))
            )
            dao = result.scalars().first()
            
            if not dao:
                raise NotFoundError(f"Customer with id {id} not found")
            return dao

    async def list_customers(self) -> List[CustomerDAO]:
        async with await self._get_session() as session:
            result = await session.execute(select(CustomerDAO).options(selectinload(CustomerDAO.loyalty_card)))
            return result.scalars().all()

    async def search_customers(
        self,
        name: Optional[str] = None,
    ) -> List[CustomerDAO]:
        async with await self._get_session() as session:
            query = select(CustomerDAO)

            # Search by name (case-insensitive partial)
            if name:
                query = query.where(CustomerDAO.name.ilike(f"%{name}%"))

            result = await session.execute(query.options(selectinload(CustomerDAO.loyalty_card)))
            return result.scalars().all()

    async def update_customer(self, customer_id: int, customer_dto: CustomerUpdateDTO) -> CustomerDAO:
        async with await self._get_session() as session:
            # load customer with loyalty card
            result = await session.execute(
                select(CustomerDAO)
                .where(CustomerDAO.id == customer_id)
                .options(selectinload(CustomerDAO.loyalty_card))
            )
            customer = result.scalars().first()

            if not customer:
                raise NotFoundError(f"Customer with id {customer_id} not found")

            # update name if provided
            update_data = customer_dto.model_dump(exclude_unset=True)
            if "name" in update_data and update_data["name"] is not None:
                customer.name = update_data["name"]

            # handle loyalty card update/attach/detach

            # if card is not provided, do nothing
            if "card" not in update_data or update_data["card"] is None:
                await session.commit()
                return await self._reload_customer(session, customer_id)

            card_payload = update_data["card"]

            # if card_payload is an empty dict, detach/delete the loyalty card
            if isinstance(card_payload, dict) and not card_payload:
                if customer.loyalty_card:
                    await session.delete(customer.loyalty_card)
                await session.commit()
                return await self._reload_customer(session, customer_id)

            # if we reach here, we have to create or update the loyalty card
            # if card_payload is provided but incomplete, raise error
            if isinstance(card_payload, dict):
                raw_card_id = card_payload.get("card_id")
                raw_points = card_payload.get("points", 0)
            else:
                # if card_payload is not a dict, try to get attributes
                raw_card_id = getattr(card_payload, "card_id", None)
                raw_points = getattr(card_payload, "points", 0)

            if raw_card_id is None:
                # if no card_id provided, do nothing
                await session.commit()
                return await self._reload_customer(session, customer_id)

            card_id = str(raw_card_id).zfill(10)
            points = int(raw_points) if raw_points is not None else 0

            if customer.loyalty_card:
                # Update existing card
                customer.loyalty_card.card_id = card_id
                customer.loyalty_card.points = points
            else:
                # Create a new card and associate it with the customer
                new_card = LoyaltyCardDAO(
                    card_id=card_id,
                    points=points,
                    customer_id=customer_id
                )
                session.add(new_card)

            await session.commit()            
            return await self._reload_customer(session, customer_id)

    async def delete_customer(self, id: int) -> None:
        async with await self._get_session() as session:
            dao = await session.get(CustomerDAO, id)
            if not dao:
                raise NotFoundError(f"Customer with id {id} not found")

            await session.delete(dao)
            await session.commit()

# ---------------------------------------------------------
    # INTERNAL: reload customer with relationship
    # ---------------------------------------------------------
    async def _reload_customer(self, session: AsyncSession, customer_id: int) -> CustomerDAO:
        result = await session.execute(
            select(CustomerDAO)
            .where(CustomerDAO.id == customer_id)
            .options(selectinload(CustomerDAO.loyalty_card))
        )
        return result.scalars().first()