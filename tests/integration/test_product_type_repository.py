import pytest
import uuid
from dataclasses import dataclass
from typing import Optional
from app.repositories.product_type_repository import ProductTypeRepository
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.shop_dao import ShopDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError

@dataclass
class MockProductData:
    barcode: str
    name: str
    description: str
    sellPrice: float
    quantity: int
    shopId: int
    discountRate: float = 0.0
    notes: Optional[str] = None

    def model_dump(self, exclude_unset=False):
        # Mimics Pydantic's model_dump for the update_product_type method
        return {k: v for k, v in self.__dict__.items() if v is not None}

@pytest.mark.asyncio
class TestProductTypeRepository:

    async def _setup_shop(self, session) -> int:
        shop = ShopDAO()
        session.add(shop)
        await session.flush()
        return shop.id

    async def test_create_product_type_success(self, db_session):
        repo = ProductTypeRepository(db_session)
        shop_id = await self._setup_shop(db_session)
        
        data = MockProductData(
            barcode=str(uuid.uuid4())[:12],
            name=f"Product-{uuid.uuid4().hex[:4]}",
            description="Test Desc",
            sellPrice=20.0,
            quantity=5,
            shopId=shop_id
        )

        created = await repo.create_product_type(data)
        assert created.id is not None
        assert created.name == data.name

    async def test_create_product_type_conflict(self, db_session):
        repo = ProductTypeRepository(db_session)
        shop_id = await self._setup_shop(db_session)
        shared_name = "UniqueName"
        
        data = MockProductData(str(uuid.uuid4())[:12], shared_name, "D", 10.0, 1, shop_id)
        await repo.create_product_type(data)

        # Attempt to create another with same name
        with pytest.raises(ConflictError):
            await repo.create_product_type(data)

    async def test_update_product_type_not_found(self, db_session):
        repo = ProductTypeRepository(db_session)
        data = MockProductData("1", "N", "D", 1.0, 1, 1)
        
        with pytest.raises(NotFoundError):
            await repo.update_product_type(9999, data)

    async def test_search_product_types_by_description(self, db_session):
        repo = ProductTypeRepository(db_session)
        shop_id = await self._setup_shop(db_session)
        
        # Create a specific item to search for
        data = MockProductData(str(uuid.uuid4())[:12], "Searchable", "FindMe", 10.0, 1, shop_id)
        await repo.create_product_type(data)

        # Search
        results = await repo.search_product_types(description="find")
        assert len(results) >= 1
        assert "FindMe" in results[0].description

    async def test_delete_product_type_success(self, db_session):
        repo = ProductTypeRepository(db_session)
        shop_id = await self._setup_shop(db_session)
        data = MockProductData(str(uuid.uuid4())[:12], "To Delete", "D", 10.0, 1, shop_id)
        
        pt = await repo.create_product_type(data)
        await repo.delete_product_type(pt.id)
        
        with pytest.raises(NotFoundError):
            await repo.delete_product_type(pt.id)