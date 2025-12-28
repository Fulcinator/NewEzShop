import pytest
from app.models.DAO.order_dao import OrderDAO
from app.repositories.order_repository import OrderRepository
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.shop_dao import ShopDAO 
from app.models.order_status import OrderStatus
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
import uuid

from tests.conftest import db_session
from tests.unit.test_sale_controller import repo

@pytest.mark.asyncio
class TestOrderRepository:

    async def _setup_product_type(self, session) -> int:
        
        shop = ShopDAO()
        session.add(shop)
        await session.flush()

        uid = uuid.uuid4().hex[:6]
        pt = ProductTypeDAO(
            barcode=f"TEST-BC-{uid}",
            name=f"Test Item {uid}",
            description="Testing stuff",
            sellPrice=49.99,
            quantity=10,
            shop_id=shop.id
        )
        session.add(pt)
        await session.commit()
        await session.refresh(pt)
        return pt.id

    async def test_issue_reorder_warning_success(self, db_session):
        repo = OrderRepository(db_session)
        pt_id = await self._setup_product_type(db_session)

        order = await repo.issue_reorder_warning(
            product_type_id=pt_id, 
            supplier="Test Supplier", 
            quantity=5, 
            price_per_unit=10.0
        )

        assert order.id is not None
        assert order.status == OrderStatus.ISSUED
        assert order.product_types[0].id == pt_id

    async def test_record_arrival_updates_inventory(self, db_session):
        repo = OrderRepository(db_session)
        pt_id = await self._setup_product_type(db_session)
        
        order = await repo.send_and_pay_order(pt_id, "Supplier", 20, 5.0)

        await repo.record_arrival(order.id)

        res = await db_session.get(ProductTypeDAO, pt_id)
        assert res.quantity == 30

    async def test_pay_issued_order_success(self, db_session):
        repo = OrderRepository(db_session)
        pt_id = await self._setup_product_type(db_session)
        order = await repo.issue_reorder_warning(pt_id, "Supplier", 10, 5.0)

        paid_order = await repo.pay_issued_order(order.id)

        assert paid_order.status == OrderStatus.PAYED

    async def test_list_orders(self, db_session):
        repo = OrderRepository(db_session)
        pt_id = await self._setup_product_type(db_session)
        await repo.issue_reorder_warning(pt_id, "Supplier A", 1, 1)

        orders = await repo.list_orders()
        assert len(orders) >= 1

    async def test_issue_reorder_warning_invalid_quantity(self, db_session):
        repo = OrderRepository(db_session)

        with pytest.raises(BadRequestError):
            await repo.issue_reorder_warning(
                product_type_id=1,
                supplier="Supplier",
                quantity=0,
                price_per_unit=10.0
            )


    async def test_issue_reorder_warning_invalid_price(self, db_session):
        repo = OrderRepository(db_session)

        with pytest.raises(BadRequestError):
            await repo.issue_reorder_warning(
                product_type_id=1,
                supplier="Supplier",
                quantity=5,
                price_per_unit=0
            )


    async def test_issue_reorder_warning_product_not_found(self, db_session):
        repo = OrderRepository(db_session)

        with pytest.raises(NotFoundError):
            await repo.issue_reorder_warning(
                product_type_id=999999,
                supplier="Supplier",
                quantity=5,
                price_per_unit=10.0
            )

    async def test_send_and_pay_order_invalid_quantity(self, db_session):
        repo = OrderRepository(db_session)

        with pytest.raises(BadRequestError):
            await repo.send_and_pay_order(
                product_type_id=1,
                supplier="Supplier",
                quantity=0,
                price_per_unit=10.0
            )


    async def test_send_and_pay_order_invalid_price(self, db_session):
        repo = OrderRepository(db_session)
        with pytest.raises(BadRequestError):
            await repo.send_and_pay_order(
                product_type_id=1,
                supplier="Supplier",
                quantity=5,
                price_per_unit=0
            )
    async def test_pay_issued_order_not_found(self, db_session):
        repo = OrderRepository(db_session)

        with pytest.raises(NotFoundError):
            await repo.pay_issued_order(999999)

    async def test_pay_issued_order_wrong_status(self, db_session):
        repo = OrderRepository(db_session)
        pt_id = await self._setup_product_type(db_session)

        order = await repo.send_and_pay_order(
            pt_id, "Supplier", 5, 10.0
        )

        with pytest.raises(BadRequestError):
            await repo.pay_issued_order(order.id)
    async def test_record_arrival_not_found(self, db_session):
        repo = OrderRepository(db_session)

        with pytest.raises(NotFoundError):
            await repo.record_arrival(999999)


    async def test_record_arrival_wrong_status(self, db_session):
        repo = OrderRepository(db_session)
        pt_id = await self._setup_product_type(db_session)

        order = await repo.issue_reorder_warning(
            pt_id, "Supplier", 5, 10.0
        )

        
        with pytest.raises(BadRequestError):
            await repo.record_arrival(order.id)



    async def test_record_arrival_no_product_types(self, db_session):
        repo = OrderRepository(db_session)

        order = OrderDAO(
            supplier="Supplier",
            status=OrderStatus.PAYED,
            quantity=5,
            price_per_unit=10.0
        )
        db_session.add(order)
        await db_session.commit()
        await db_session.refresh(order)

        with pytest.raises(BadRequestError):
            await repo.record_arrival(order.id)


