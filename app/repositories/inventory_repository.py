from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import AsyncSessionLocal
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.position_dao import PositionDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError

class InventoryRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def update_quantity(self, product_type_id: int, new_quantity: int) -> ProductTypeDAO:
        if new_quantity < 0:
            raise BadRequestError("Quantity cannot be negative")

        async with await self._get_session() as session:
            pt = await session.get(ProductTypeDAO, product_type_id)
            if not pt:
                raise NotFoundError(f"Product type with id '{product_type_id}' not found")

            pt.quantity = new_quantity
            await session.commit()
            await session.refresh(pt)
            return pt

    async def update_position(
        self, product_type_id: int, aisleID: int, rackID: int, levelID: int
    ) -> ProductTypeDAO:
        async with await self._get_session() as session:
            pt = await session.get(ProductTypeDAO, product_type_id)
            if not pt:
                raise NotFoundError(f"Product type with id '{product_type_id}' not found")

            # creating the position if it does not exist
            if pt.position is None:
                position = PositionDAO(aisleID=aisleID, rackID=rackID, levelID=levelID)
                session.add(position)
                await session.flush()
                pt.position = position
            else:
                pt.position.aisleID = aisleID
                pt.position.rackID = rackID
                pt.position.levelID = levelID

            await session.commit()
            await session.refresh(pt)
            return pt
