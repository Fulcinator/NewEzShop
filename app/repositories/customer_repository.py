from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import AsyncSessionLocal
from app.models.DAO.customer_dao import CustomerDAO
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
                    (CustomerDAO.name == data.name) &
                    (CustomerDAO.surname == data.surname)
                )
            )
            existing = result.scalars().first()
            if existing:
                raise ConflictError("Customer with same name and surname already exists")
            
            dao = CustomerDAO(
                name=data.name,
                surname=data.surname
            )
            
            session.add(dao)
            await session.commit()
            await session.refresh(dao)
            return dao

    async def get_customer_by_id(self, id: int) -> CustomerDAO:
        async with await self._get_session() as session:
            dao = await session.get(CustomerDAO, id)
            
            if not dao:
                raise NotFoundError(f"Customer with id {id} not found")
            
            return dao

    async def list_customers(self) -> List[CustomerDAO]:
        async with await self._get_session() as session:
            result = await session.execute(select(CustomerDAO))
            return result.scalars().all()

    async def search_customers(
        self,
        name: Optional[str] = None,
        surname: Optional[str] = None
    ) -> List[CustomerDAO]:
        async with await self._get_session() as session:
            query = select(CustomerDAO)

            # Search by name (case-insensitive partial)
            if name:
                query = query.where(CustomerDAO.name.ilike(f"%{name}%"))

            # Search by surname (case-insensitive partial)
            if surname:
                query = query.where(CustomerDAO.surname.ilike(f"%{surname}%"))

            result = await session.execute(query)
            return result.scalars().all()

    async def update_customer(self, id: int, data) -> CustomerDAO:
        async with await self._get_session() as session:
            dao = await session.get(CustomerDAO, id)
            
            if not dao:
                raise NotFoundError(f"Customer with id {id} not found")

            # Update only provided fields in DTO
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(dao, field, value)

            await session.commit()
            await session.refresh(dao)
            return dao

    async def delete_customer(self, id: int) -> None:
        async with await self._get_session() as session:
            dao = await session.get(CustomerDAO, id)
            if not dao:
                raise NotFoundError(f"Customer with id {id} not found")

            await session.delete(dao)
            await session.commit()
