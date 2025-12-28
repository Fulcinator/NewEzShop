import pytest
import uuid
from app.repositories.inventory_repository import InventoryRepository
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.shop_dao import ShopDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError

@pytest.mark.asyncio
class TestInventoryRepository:

    async def _setup_product_type(self, session) -> int:
        shop = ShopDAO()
        session.add(shop)
        await session.flush()
        
        uid = uuid.uuid4().hex[:6]
        pt = ProductTypeDAO(
            barcode=f"INV-{uid}",
            name=f"Inv Item {uid}",
            sellPrice=5.0,
            quantity=50,
            shop_id=shop.id
        )
        session.add(pt)
        await session.commit()
        return pt.id


    async def test_update_quantity_success(self, db_session):
        repo = InventoryRepository(db_session)
        pt_id = await self._setup_product_type(db_session)

        updated_pt = await repo.update_quantity(pt_id, 100)

        assert updated_pt.quantity == 100
        # Double check DB state
        res = await db_session.get(ProductTypeDAO, pt_id)
        assert res.quantity == 100

    async def test_update_quantity_negative_fails(self, db_session):
        repo = InventoryRepository(db_session)
        pt_id = await self._setup_product_type(db_session)

        with pytest.raises(BadRequestError, match="Quantity cannot be negative"):
            await repo.update_quantity(pt_id, -1)


    async def test_update_position_creates_new_position(self, db_session):
        repo = InventoryRepository(db_session)
        pt_id = await self._setup_product_type(db_session)

        updated_pt = await repo.update_position(pt_id, 1, 2, 3)

        assert updated_pt.position is not None
        assert updated_pt.position.aisleID == 1
        assert updated_pt.position.rackID == 2

    async def test_update_position_updates_existing(self, db_session):
        repo = InventoryRepository(db_session)
        pt_id = await self._setup_product_type(db_session)

        await repo.update_position(pt_id, 1, 1, 1)

        updated_pt = await repo.update_position(pt_id, 5, 5, 5)

        assert updated_pt.position.aisleID == 5

    async def test_inventory_not_found(self, db_session):
        repo = InventoryRepository(db_session)
        
        with pytest.raises(NotFoundError):
            await repo.update_quantity(9999, 10)