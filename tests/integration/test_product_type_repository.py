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
        
        data = MockProductData(str(uuid.uuid4())[:12], "Searchable", "FindMe", 10.0, 1, shop_id)
        await repo.create_product_type(data)

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

    async def test_update_product_type_success(self, db_session):
        repo = ProductTypeRepository(db_session)
        shop_id = await self._setup_shop(db_session)

        data = MockProductData(
            barcode=str(uuid.uuid4())[:12],
            name="Original",
            description="Old desc",
            sellPrice=10.0,
            quantity=5,
            shopId=shop_id
        )

        created = await repo.create_product_type(data)

        update_data = MockProductData(
            barcode=None,             
            name="Updated Name",       
            description=None,
            sellPrice=15.0,            
            quantity=None,
            shopId=None
        )

        updated = await repo.update_product_type(created.id, update_data)

        assert updated.id == created.id
        assert updated.name == "Updated Name"
        assert updated.sellPrice == 15.0
        assert updated.description == "Old desc"   

    async def test_list_product_types(self, db_session):
        repo = ProductTypeRepository(db_session)
        shop_id = await self._setup_shop(db_session)

        await repo.create_product_type(
            MockProductData(str(uuid.uuid4())[:12], "P1", "D1", 10.0, 1, shop_id)
        )
        await repo.create_product_type(
            MockProductData(str(uuid.uuid4())[:12], "P2", "D2", 20.0, 2, shop_id)
        )

        products = await repo.list_product_types()

        assert len(products) >= 2
        assert all(isinstance(p, ProductTypeDAO) for p in products)
    async def test_search_product_types_by_barcode(self, db_session):
        repo = ProductTypeRepository(db_session)
        shop_id = await self._setup_shop(db_session)

        target_barcode = str(uuid.uuid4())[:12]

        matching = MockProductData(
            barcode=target_barcode,
            name="BarcodeMatch",
            description="Something",
            sellPrice=10.0,
            quantity=1,
            shopId=shop_id
        )

        non_matching = MockProductData(
            barcode=str(uuid.uuid4())[:12],
            name="Other",
            description="Something",
            sellPrice=10.0,
            quantity=1,
            shopId=shop_id
        )

        await repo.create_product_type(matching)
        await repo.create_product_type(non_matching)

        results = await repo.search_product_types(barcode=target_barcode)

        assert len(results) == 1
        assert results[0].barcode == target_barcode
