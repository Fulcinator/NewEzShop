from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload

from app.database.database import AsyncSessionLocal
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.product_dao import ProductDAO
from app.models.DAO.position_dao import PositionDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.bad_request import BadRequestError


class ProductTypeRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self):
        return self._session or AsyncSessionLocal()

    def _parse_position_string(self, pos_str: str) -> tuple[int, str, int]:
        try:
            aisle, rack, level = pos_str.split("-")
            return int(aisle), rack, int(level)
        except Exception:
            raise ConflictError("Invalid position format. Expected format: '1-A-3'")

    async def create_product_type(self, data) -> ProductTypeDAO:
        async with await self._get_session() as session:
            # Note: Barcode uniqueness is NOT enforced at creation time
            # Multiple products can share the same barcode
            
            # 2. Handle position (optional)
            position_id = None
            if data.position:
                # Parse position string
                aisleID, rackID, levelID = self._parse_position_string(data.position)

                # Check if position already occupied
                pos_query = await session.execute(
                    select(PositionDAO).where(
                        and_(
                            PositionDAO.aisleID == aisleID,
                            PositionDAO.rackID == rackID,
                            PositionDAO.levelID == levelID
                        )
                    )
                )
                if pos_query.scalars().first():
                    raise ConflictError("Position already occupied")

                # Create PositionDAO
                position = PositionDAO(
                    aisleID=aisleID,
                    rackID=rackID,
                    levelID=levelID
                )
                session.add(position)
                await session.flush()  # ensures position.id is available
                position_id = position.id

            # 3. Create ProductTypeDAO
            dao = ProductTypeDAO(
                barcode=data.barcode,
                description=data.description,
                price_per_unit=data.price_per_unit,
                quantity=data.quantity if data.quantity is not None else 0,
                # discountRate is applied on sale transaction level
                discountRate=data.discountRate if data.discountRate is not None else 0.0,
                note=data.note,
                shop_id=1, # default shop
                position_id=position_id,
            )
            session.add(dao)
            await session.flush()  # ensures dao.id is available

            # 6. Create ProductDAO (single physical product)
            product = ProductDAO(product_type_id=dao.id)
            session.add(product)

            # 7. Commit
            await session.commit()

            # 8. Reload with position eagerly loaded
            result = await session.execute(
                select(ProductTypeDAO)
                .options(selectinload(ProductTypeDAO.position))
                .where(ProductTypeDAO.id == dao.id)
            )
            dao = result.scalars().first()
            return dao

    async def get_product_type_by_id(self, id: int) -> ProductTypeDAO:
        async with await self._get_session() as session:
            result = await session.execute(
                select(ProductTypeDAO)
                .options(selectinload(ProductTypeDAO.position))
                .where(ProductTypeDAO.id == id)
            )
            dao = result.scalars().first()
            if not dao:
                raise NotFoundError(f"Product type with id {id} not found")
            return dao
    
    async def update_product_type(self, id: int, data) -> ProductTypeDAO:
        async with await self._get_session() as session:
            dao = await session.get(ProductTypeDAO, id, options=[selectinload(ProductTypeDAO.position)])
            if not dao:
                raise NotFoundError(f"Product type with id {id} not found")

            update_data = data.model_dump(exclude_unset=True)
            
            # Handle barcode updates
            if "barcode" in update_data:
                new_barcode = update_data["barcode"]
                
                # Check barcode conflicts FIRST (409 takes precedence over 400)
                # Check for conflicts even if barcode isn't changing, to detect other products with same barcode
                barcode_check = await session.execute(
                    select(ProductTypeDAO).where(
                        and_(
                            ProductTypeDAO.barcode == new_barcode,
                            ProductTypeDAO.id != id
                        )
                    )
                )
                if barcode_check.scalar_one_or_none():
                    raise ConflictError("Product type with same barcode already exists")
                
                # GS1 barcode validation (NFR4 requirement) - only if barcode is actually changing
                if new_barcode is not None and new_barcode != dao.barcode:
                    if not self._validate_gs1_check_digit(new_barcode):
                        raise BadRequestError("Invalid barcode check digit")
            # handle position update separately
            if "position" in update_data:
                new_pos_str = update_data["position"]
                # If new position is None, remove position
                if new_pos_str is None:
                    if dao.position:
                        await session.delete(dao.position)
                        dao.position_id = None
                else:
                    aisleID, rackID, levelID = self._parse_position_string(new_pos_str)

                    # Check if new position is already occupied
                    pos_query = await session.execute(
                        select(PositionDAO).where(
                            and_(
                                PositionDAO.aisleID == aisleID,
                                PositionDAO.rackID == rackID,
                                PositionDAO.levelID == levelID,
                                PositionDAO.id != dao.position_id  # exclude the current position
                            )
                        )
                    )
                    if pos_query.scalars().first():
                        raise ConflictError("New position is already occupied")

                    # Update or create position
                    if dao.position:
                        dao.position.aisleID = aisleID
                        dao.position.rackID = rackID
                        dao.position.levelID = levelID
                    else:
                        # Create new position
                        new_position = PositionDAO(
                            aisleID=aisleID,
                            rackID=rackID,
                            levelID=levelID
                        )
                        session.add(new_position)
                        await session.flush()
                        dao.position_id = new_position.id

            # Update other fields of the product type (excluding position)
            for field, value in update_data.items():
                if field == "position":
                    continue
                setattr(dao, field, value)

            await session.commit()
            # reload with position
            result = await session.execute(
                select(ProductTypeDAO)
                .options(selectinload(ProductTypeDAO.position))
                .where(ProductTypeDAO.id == id)
            )
            return result.scalars().first()

    async def delete_product_type(self, id: int) -> None:
        async with await self._get_session() as session:
            dao = await session.get(ProductTypeDAO, id)
            if not dao:
                raise NotFoundError(f"Product type with id {id} not found")
            
            await session.delete(dao)
            await session.commit()

    async def list_product_types(self) -> List[ProductTypeDAO]:
        async with await self._get_session() as session:
            result = await session.execute(select(ProductTypeDAO).options(selectinload(ProductTypeDAO.position)))
            return result.scalars().all()

    async def get_product_type_by_barcode(self, barcode: str) -> ProductTypeDAO:
        async with await self._get_session() as session:
            result = await session.execute(
                select(ProductTypeDAO)
                .options(selectinload(ProductTypeDAO.position))
                .where(ProductTypeDAO.barcode == barcode)
            )
            dao = result.scalars().first()
            if not dao:
                raise NotFoundError(f"Product type with barcode {barcode} not found")
            return dao

    async def search_product_types(
        self,
        barcode: Optional[str] = None,
        description: Optional[str] = None
    ) -> List[ProductTypeDAO]:
        async with await self._get_session() as session:
            query = select(ProductTypeDAO).options(selectinload(ProductTypeDAO.position))

            # Search by barcode
            if barcode:
                query = query.where(ProductTypeDAO.barcode == barcode)

            # Search by description (partial match)
            if description:
                query = query.where(ProductTypeDAO.description.ilike(f"%{description}%"))

            result = await session.execute(query)
            return result.scalars().all()

    async def patch_position(self, id: int, position_str: Optional[str]) -> None:
        async with await self._get_session() as session:
            dao = await session.get(
                ProductTypeDAO,
                id,
                options=[selectinload(ProductTypeDAO.position)]
            )
            if not dao:
                raise NotFoundError(f"Product type with id {id} not found")

            # Handle empty string or None to unset position
            if not position_str:
                if dao.position:
                    await session.delete(dao.position)
                    dao.position_id = None
                await session.commit()
                return
            
            # Parse and validate new position
            aisleID, rackID, levelID = self._parse_position_string(position_str)

            pos_query = await session.execute(
                select(PositionDAO).where(
                    and_(
                        PositionDAO.aisleID == aisleID,
                        PositionDAO.rackID == rackID,
                        PositionDAO.levelID == levelID,
                        PositionDAO.id != dao.position_id
                    )
                )
            )
            if pos_query.scalars().first():
                raise ConflictError("Position already occupied")

            if dao.position:
                dao.position.aisleID = aisleID
                dao.position.rackID = rackID
                dao.position.levelID = levelID
            else:
                new_position = PositionDAO(
                    aisleID=aisleID,
                    rackID=rackID,
                    levelID=levelID
                )
                session.add(new_position)
                await session.flush()
                dao.position_id = new_position.id

            await session.commit()

    async def patch_quantity(self, id: int, new_quantity: int) -> None:
        async with await self._get_session() as session:
            dao = await session.get(ProductTypeDAO, id)
            if not dao:
                raise NotFoundError(f"Product type with id {id} not found")

            if new_quantity < 0:
                raise ConflictError("Quantity cannot be negative")

            dao.quantity = new_quantity
            await session.commit()

    @staticmethod
    def _validate_gs1_check_digit(barcode: str) -> bool:
        """Validate GS1 check digit according to NFR4 requirement"""
        if len(barcode) < 12:
            return False
            
        # Extract the data digits (all except the last one which is the check digit)
        data_digits = barcode[:-1]
        check_digit = int(barcode[-1])
        
        # Calculate check digit using GS1 algorithm
        odd_sum = sum(int(data_digits[i]) for i in range(0, len(data_digits), 2))
        even_sum = sum(int(data_digits[i]) for i in range(1, len(data_digits), 2))
        
        total = odd_sum + (even_sum * 3)
        calculated_check_digit = (10 - (total % 10)) % 10
        
        return check_digit == calculated_check_digit