import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from app.database.database import AsyncSessionLocal
from app.models.DAO.order_productType_association import order_productType_association
from app.models.errors.bad_request import BadRequestError
from app.repositories.order_repository import OrderRepository
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.balanceOperation_dao import BalanceOperationDAO
from app.models.order_status import OrderStatus
from app.models.errors.balance_error import BalanceError
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.ordes_errors import GeneralError, InvalidStateError


# ---------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------

@pytest.fixture
async def session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def repo(session) -> OrderRepository:
    return OrderRepository(session)

@pytest.fixture(autouse=True)
async def clean_db():
    from app.database import database
    await database.reset_db()
    await database.init_db()



async def seed_product(session, *, barcode: str, quantity: int = 10):
    # First create the position
    from app.models.DAO.position_dao import PositionDAO
    position = PositionDAO(
        aisleID=1,
        rackID="A",
        levelID=1
    )
    session.add(position)
    await session.flush()  # Ensure position ID is available
    
    # Then create the product with position_id
    product = ProductTypeDAO(
        barcode=barcode,
        price_per_unit=10.0,
        quantity=quantity,
        shop_id=1,
        position_id=position.id
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product




from app.models.DAO.system_dao import SystemInfoDAO

async def seed_balance(session, amount: float):
    sys = await session.execute(select(SystemInfoDAO))
    sys = sys.scalar_one_or_none()

    if not sys:
        sys = SystemInfoDAO(balance=amount)
        session.add(sys)
    else:
        sys.balance = amount

    await session.commit()


# =====================================================================
# TESTS
# =====================================================================

@pytest.mark.asyncio
async def test_issue_reorder_warning(repo, session):
    product = await seed_product(session, barcode="123456789001")

    order = await repo.issue_reorder_warning(
        product_barcode=product.barcode,
        quantity=5,
        price_per_unit=50.0,
    )

    assert order.status == OrderStatus.ISSUED
    assert order.quantity == 5
    assert order.product_types[0].barcode == "123456789001"


@pytest.mark.asyncio
async def test_issue_reorder_warning_product_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.issue_reorder_warning(
            product_barcode="UNKNOWN",
            quantity=1,
            price_per_unit=10.0,
        )


@pytest.mark.asyncio
async def test_create_and_pay_order_success(repo, session):
    product = await seed_product(session, barcode="123456789002")
    await seed_balance(session, amount=10_000)

    order = await repo.create_and_pay_order(
        product_barcode=product.barcode,
        quantity=2,
        price_per_unit=100.0,
    )

    assert order.status == OrderStatus.PAYED
    assert order.product_types[0].barcode == "123456789002"


@pytest.mark.asyncio
async def test_create_and_pay_order_insufficient_balance(repo, session):
    product = await seed_product(session, barcode="123456789003")

    with pytest.raises(BalanceError):
        await repo.create_and_pay_order(
            product_barcode=product.barcode,
            quantity=10,
            price_per_unit=500.0,
        )


@pytest.mark.asyncio
async def test_pay_issued_and_update_balance_success(repo, session):
    product = await seed_product(session, barcode="123456789004")
    await seed_balance(session, amount=10_000)

    order = await repo.issue_reorder_warning(
        product_barcode=product.barcode,
        quantity=3,
        price_per_unit=200.0,
    )

    await repo.pay_issued_and_update_balance(order.id)

    refreshed = await session.get(type(order), order.id)
    assert refreshed.status == OrderStatus.PAYED


@pytest.mark.asyncio
async def test_pay_issued_invalid_state(repo, session):
    product = await seed_product(session, barcode="123456789005")
    await seed_balance(session, amount=10_000)

    order = await repo.create_and_pay_order(
        product_barcode=product.barcode,
        quantity=1,
        price_per_unit=100.0,
    )

    with pytest.raises(InvalidStateError):
        await repo.pay_issued_and_update_balance(order.id)


@pytest.mark.asyncio
async def test_record_arrival_and_update_quantity(repo, session):
    product = await seed_product(session, barcode="123456789006", quantity=10)
    await seed_balance(session, amount=10_000)

    order = await repo.create_and_pay_order(
        product_barcode=product.barcode,
        quantity=5,
        price_per_unit=100.0,
    )

    await repo.record_arrival_and_update_quantity(order.id)

    updated_product = await session.get(ProductTypeDAO, product.id)
    updated_order = await session.get(type(order), order.id)

    assert updated_product.quantity == 15
    assert updated_order.status == OrderStatus.COMPLETED


@pytest.mark.asyncio
async def test_list_orders(repo, session):
    product = await seed_product(session, barcode="123456789007")
    await seed_balance(session, amount=10_000)

    await repo.issue_reorder_warning(
        product_barcode=product.barcode,
        quantity=1,
        price_per_unit=10.0,
    )

    orders = await repo.list_orders()
    assert len(orders) >= 1

@pytest.mark.asyncio
async def test_issue_reorder_warning_invalid_quantity(repo):
    with pytest.raises(BadRequestError):
        await repo.issue_reorder_warning("ANY", 0, 10.0)

@pytest.mark.asyncio
async def test_issue_reorder_warning_invalid_price(repo):
    with pytest.raises(BadRequestError):
        await repo.issue_reorder_warning("ANY", 1, 0)

@pytest.mark.asyncio
async def test_create_and_pay_order_invalid_quantity(repo, session):
    product = await seed_product(session, barcode="123456789008")
    await seed_balance(session, 10_000)

    with pytest.raises(BadRequestError):
        await repo.create_and_pay_order(product.barcode, 0, 10)

@pytest.mark.asyncio
async def test_create_and_pay_order_invalid_price(repo, session):
    product = await seed_product(session, barcode="123456789009")
    await seed_balance(session, 10_000)

    with pytest.raises(BadRequestError):
        await repo.create_and_pay_order(product.barcode, 1, 0)

@pytest.mark.asyncio
async def test_pay_issued_order_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.pay_issued_and_update_balance(999)


@pytest.mark.asyncio
async def test_record_arrival_order_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.record_arrival_and_update_quantity(999)

@pytest.mark.asyncio
async def test_list_orders_with_status_filter(repo, session):
    product = await seed_product(session, barcode="123456789010")
    await seed_balance(session, amount=10_000)

    issued = await repo.issue_reorder_warning(
        product_barcode=product.barcode,
        quantity=1,
        price_per_unit=10.0,
    )

    paid = await repo.create_and_pay_order(
        product_barcode=product.barcode,
        quantity=1,
        price_per_unit=10.0,
    )

    issued_orders = await repo.list_orders(status=OrderStatus.ISSUED)
    paid_orders = await repo.list_orders(status=OrderStatus.PAYED)

    assert all(o.status == OrderStatus.ISSUED for o in issued_orders)
    assert all(o.status == OrderStatus.PAYED for o in paid_orders)

@pytest.mark.asyncio
async def test_create_and_pay_order_product_type_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.create_and_pay_order(
            product_barcode="DOES-NOT-EXIST",
            quantity=1,
            price_per_unit=10.0,
        )

@pytest.mark.asyncio
async def test_issue_reorder_warning_product_barcode_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.issue_reorder_warning(
            product_barcode="UNKNOWN",
            quantity=5,
            price_per_unit=10.0,
        )

@pytest.mark.asyncio
async def test_pay_issued_order_without_product_type(repo, session):
    product = await seed_product(session, barcode="123456789011")
    await seed_balance(session, amount=10_000)

    order = await repo.issue_reorder_warning(
        product_barcode=product.barcode,
        quantity=1,
        price_per_unit=10.0,
    )

    # 🔥 REMOVE association row at DB level
    await session.execute(
        delete(order_productType_association).where(
            order_productType_association.c.order_id == order.id
        )
    )
    await session.commit()

    with pytest.raises(GeneralError):
        await repo.pay_issued_and_update_balance(order.id)

@pytest.mark.asyncio
async def test_record_arrival_without_product_type(repo, session):
    product = await seed_product(session, barcode="123456789012")
    await seed_balance(session, amount=10_000)

    order = await repo.create_and_pay_order(
        product_barcode=product.barcode,
        quantity=1,
        price_per_unit=10.0,
    )

    await session.execute(
        delete(order_productType_association).where(
            order_productType_association.c.order_id == order.id
        )
    )
    await session.commit()

    with pytest.raises(GeneralError):
        await repo.record_arrival_and_update_quantity(order.id)


@pytest.mark.asyncio
async def test_pay_issued_order_insufficient_balance(repo, session):
    product = await seed_product(session, barcode="123456789013")

    order = await repo.issue_reorder_warning(
        product_barcode=product.barcode,
        quantity=5,
        price_per_unit=100.0,
    )

    # NO system balance seeded

    with pytest.raises(BalanceError):
        await repo.pay_issued_and_update_balance(order.id)

@pytest.mark.asyncio
async def test_pay_issued_order_invalid_state_completed(repo, session):
    product = await seed_product(session, barcode="123456789014")
    await seed_balance(session, amount=10_000)

    order = await repo.create_and_pay_order(
        product_barcode=product.barcode,
        quantity=1,
        price_per_unit=10.0,
    )

    await repo.record_arrival_and_update_quantity(order.id)

    with pytest.raises(InvalidStateError):
        await repo.pay_issued_and_update_balance(order.id)
