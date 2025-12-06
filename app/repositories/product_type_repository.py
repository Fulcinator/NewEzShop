from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import AsyncSessionLocal
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError


class ProductTypeRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self):
        return self._session or AsyncSessionLocal()

    async def create_product_type(self, data) -> ProductTypeDAO:
        async with await self._get_session() as session:
            # Conflict checking
            result = await session.execute(
                select(ProductTypeDAO).where(
                    (ProductTypeDAO.barcode == data.barcode) |
                    (ProductTypeDAO.name == data.name)
                )
            )
            existing = result.scalars().first()
            if existing:
                raise ConflictError("Product type with same name or barcode already exists")

            dao = ProductTypeDAO(
                barcode=data.barcode,
                name=data.name,
                description=data.description,
                sellPrice=data.sellPrice,
                quantity=data.quantity,
                discountRate=data.discountRate,
                notes=data.notes,
                shop_id=data.shopId
            )
            session.add(dao)
            await session.commit()
            await session.refresh(dao)
            return dao

    async def update_product_type(self, id: int, data) -> ProductTypeDAO:
        async with await self._get_session() as session:
            dao = await session.get(ProductTypeDAO, id)
            if not dao:
                raise NotFoundError(f"Product type with id {id} not found")

            # Only update provided fields
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(dao, field, value)

            await session.commit()
            await session.refresh(dao)
            return dao

    async def delete_product_type(self, id: int) -> None:
        async with await self._get_session() as session:
            dao = await session.get(ProductTypeDAO, id)
            if not dao:
                raise NotFoundError(f"Product type with id {id} not found")

            await session.delete(dao)
            await session.commit()

    async def list_product_types(self) -> List[ProductTypeDAO]:
        async with await self._get_session() as session:
            result = await session.execute(select(ProductTypeDAO))
            return result.scalars().all()

    async def search_product_types(
        self,
        barcode: Optional[str] = None,
        description: Optional[str] = None
    ) -> List[ProductTypeDAO]:
        async with await self._get_session() as session:
            query = select(ProductTypeDAO)

            # Search by barcode
            if barcode:
                query = query.where(ProductTypeDAO.barcode == barcode)

            # Search by description (partial match)
            if description:
                query = query.where(ProductTypeDAO.description.ilike(f"%{description}%"))

            result = await session.execute(query)
            return result.scalars().all()

