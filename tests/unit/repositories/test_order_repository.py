import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.repositories.order_repository import OrderRepository
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.balanceOperation_dao import BalanceOperationDAO
from app.models.order_status import OrderStatus
from app.models.errors.balance_error import BalanceError
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.ordes_errors import InvalidStateError


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
    product = ProductTypeDAO(
        barcode=barcode,
        price_per_unit=10.0,
        quantity=quantity,
        shop_id=1,     
        position=None     
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product





async def seed_balance(session, amount: float):
    session.add(
        BalanceOperationDAO(
            amount=amount,
            date=datetime.utcnow(),
            account_book_id=1,
        )
    )
    await session.commit()


# =====================================================================
# TESTS
# =====================================================================

@pytest.mark.asyncio
async def test_issue_reorder_warning(repo, session):
    product = await seed_product(session, barcode="P-TEST1")

    order = await repo.issue_reorder_warning(
        product_barcode=product.barcode,
        quantity=5,
        price_per_unit=50.0,
    )

    assert order.status == OrderStatus.ISSUED
    assert order.quantity == 5
    assert order.product_types[0].barcode == "P-TEST1"


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
    product = await seed_product(session, barcode="P-PAY")
    await seed_balance(session, amount=10_000)

    order = await repo.create_and_pay_order(
        product_barcode=product.barcode,
        quantity=2,
        price_per_unit=100.0,
    )

    assert order.status == OrderStatus.PAYED
    assert order.product_types[0].barcode == "P-PAY"


@pytest.mark.asyncio
async def test_create_and_pay_order_insufficient_balance(repo, session):
    product = await seed_product(session, barcode="P-NOBAL")

    with pytest.raises(BalanceError):
        await repo.create_and_pay_order(
            product_barcode=product.barcode,
            quantity=10,
            price_per_unit=500.0,
        )


@pytest.mark.asyncio
async def test_pay_issued_and_update_balance_success(repo, session):
    product = await seed_product(session, barcode="P-PAY2")
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
    product = await seed_product(session, barcode="P-BADSTATE")
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
    product = await seed_product(session, barcode="P-ARR", quantity=10)
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
    product = await seed_product(session, barcode="P-LIST")
    await seed_balance(session, amount=10_000)

    await repo.issue_reorder_warning(
        product_barcode=product.barcode,
        quantity=1,
        price_per_unit=10.0,
    )

    orders = await repo.list_orders()
    assert len(orders) >= 1
