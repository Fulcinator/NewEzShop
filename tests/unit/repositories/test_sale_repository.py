import pytest
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import AsyncSessionLocal
from app.repositories.sale_repository import SaleRepository

from app.models.DAO.saleTransaction_dao import SaleTransactionDAO
from app.models.DAO.sale_product_association import SaleProductAssociation
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.system_dao import SystemInfoDAO
from app.models.DAO.balanceOperation_dao import BalanceOperationDAO

from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.invalid_state_error import InvalidStateError


# ---------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------

@pytest.fixture(autouse=True)
async def reset_db():
    from app.database import database
    await database.reset_db()
    await database.init_db()


@pytest.fixture
async def session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def repo(session) -> SaleRepository:
    return SaleRepository(session)


# ---------------------------------------------------------------------
# SEED HELPERS
# ---------------------------------------------------------------------

async def seed_product(
    session,
    *,
    barcode: str,
    quantity: int = 10,
    price: float = 5.0
):
    product = ProductTypeDAO(
        barcode=barcode,
        description=barcode,
        price_per_unit=price,
        quantity=quantity,
        discountRate=0.0,
        shop_id=1,
    )
    session.add(product)
    await session.commit()
    return product


async def seed_sale(session, status="OPEN"):
    sale = SaleTransactionDAO(
        status=status,
        created_at=datetime.utcnow(),
        discountRate=0.0,
    )
    session.add(sale)
    await session.commit()
    return sale


async def seed_system(session, balance=0.0):
    sys = SystemInfoDAO(balance=balance)
    session.add(sys)
    await session.commit()
    return sys


# =====================================================================
# TESTS
# =====================================================================

@pytest.mark.asyncio
async def test_create_and_get_sale(repo, session):
    sale = await repo.create_sale({"status": "OPEN"})
    fetched = await repo.get_sale_by_id(sale.id)

    assert fetched.id == sale.id
    assert fetched.status == "OPEN"


@pytest.mark.asyncio
async def test_get_all_sales(repo, session):
    await seed_sale(session)
    await seed_sale(session)

    sales = await repo.get_all_sales()
    assert len(sales) == 2


@pytest.mark.asyncio
async def test_add_product_to_sale(repo, session):
    sale = await seed_sale(session)
    product = await seed_product(session, barcode="P-ADD", quantity=10)

    await repo.add_product_to_sale(sale.id, product.barcode, 3)

    line = (
        await session.execute(
            select(SaleProductAssociation)
        )
    ).scalar_one()

    updated_product = await session.get(ProductTypeDAO, product.id)

    assert line.quantity == 3
    assert updated_product.quantity == 7


@pytest.mark.asyncio
async def test_add_product_insufficient_stock(repo, session):
    sale = await seed_sale(session)
    product = await seed_product(session, barcode="P-NO", quantity=1)

    with pytest.raises(BadRequestError):
        await repo.add_product_to_sale(sale.id, product.barcode, 5)


@pytest.mark.asyncio
async def test_remove_product_from_sale(repo, session):
    sale = await seed_sale(session)
    product = await seed_product(session, barcode="P-REM", quantity=10)

    await repo.add_product_to_sale(sale.id, product.barcode, 4)
    await repo.remove_product_from_sale(sale.id, product.barcode, 2)

    line = (
        await session.execute(select(SaleProductAssociation))
    ).scalar_one()

    updated_product = await session.get(ProductTypeDAO, product.id)

    assert line.quantity == 2
    assert updated_product.quantity == 8


@pytest.mark.asyncio
async def test_apply_discount_to_sale(repo, session):
    sale = await seed_sale(session)

    updated = await repo.apply_discount_to_sale(sale.id, 0.2)
    assert updated.discountRate == 0.2


@pytest.mark.asyncio
async def test_apply_discount_invalid_rate(repo, session):
    sale = await seed_sale(session)

    with pytest.raises(BadRequestError):
        await repo.apply_discount_to_sale(sale.id, 1.5)


@pytest.mark.asyncio
async def test_close_empty_sale_deletes(repo, session):
    sale = await seed_sale(session)

    result = await repo.close_sale(sale.id)
    assert result == {"deleted": True}

    assert await repo.get_sale_by_id(sale.id) is None


@pytest.mark.asyncio
async def test_close_sale_with_lines(repo, session):
    sale = await seed_sale(session)
    product = await seed_product(session, barcode="P-CLOSE")

    await repo.add_product_to_sale(sale.id, product.barcode, 1)
    await repo.close_sale(sale.id)

    updated = await repo.get_sale_by_id(sale.id)
    assert updated.status == "PENDING"


@pytest.mark.asyncio
async def test_pay_sale(repo, session):
    await seed_system(session, balance=0.0)
    sale = await seed_sale(session)
    product = await seed_product(session, barcode="P-PAY", price=10)

    await repo.add_product_to_sale(sale.id, product.barcode, 2)
    await repo.close_sale(sale.id)

    result = await repo.pay_sale(sale.id, cash_amount=25.0)
    assert result["change"] == 5.0

    paid = await repo.get_sale_by_id(sale.id)
    assert paid.status == "PAID"


@pytest.mark.asyncio
async def test_compute_points(repo, session):
    await seed_system(session)
    sale = await seed_sale(session)
    product = await seed_product(session, barcode="P-PTS", price=3)

    await repo.add_product_to_sale(sale.id, product.barcode, 4)
    await repo.close_sale(sale.id)
    await repo.pay_sale(sale.id, cash_amount=20)

    result = await repo.compute_points(sale.id)
    assert result["points"] == 12


@pytest.mark.asyncio
async def test_compute_points_invalid_state(repo, session):
    sale = await seed_sale(session)

    with pytest.raises(InvalidStateError):
        await repo.compute_points(sale.id)

@pytest.mark.asyncio
async def test_get_product_by_barcode_not_found(repo):
    product = await repo.get_product_by_barcode("UNKNOWN")
    assert product is None

@pytest.mark.asyncio
async def test_delete_sale_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.delete_sale(999)


@pytest.mark.asyncio
async def test_delete_paid_sale_raises(repo, session):
    sale = await seed_sale(session, status="PAID")

    with pytest.raises(InvalidStateError):
        await repo.delete_sale(sale.id)

@pytest.mark.asyncio
async def test_add_product_sale_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.add_product_to_sale(999, "X", 1)


@pytest.mark.asyncio
async def test_add_product_sale_not_open(repo, session):
    sale = await seed_sale(session, status="PENDING")
    product = await seed_product(session, barcode="X")

    with pytest.raises(InvalidStateError):
        await repo.add_product_to_sale(sale.id, product.barcode, 1)


@pytest.mark.asyncio
async def test_add_product_product_not_found(repo, session):
    sale = await seed_sale(session)

    with pytest.raises(NotFoundError):
        await repo.add_product_to_sale(sale.id, "UNKNOWN", 1)

@pytest.mark.asyncio
async def test_remove_product_not_in_sale(repo, session):
    sale = await seed_sale(session)
    product = await seed_product(session, barcode="X")

    with pytest.raises(NotFoundError):
        await repo.remove_product_from_sale(sale.id, product.barcode, 1)

@pytest.mark.asyncio
async def test_apply_discount_product_not_in_sale(repo, session):
    sale = await seed_sale(session)
    product = await seed_product(session, barcode="X")

    with pytest.raises(NotFoundError):
        await repo.apply_discount_to_product(sale.id, product.barcode, 0.2)

@pytest.mark.asyncio
async def test_pay_sale_invalid_state(repo, session):
    sale = await seed_sale(session)

    with pytest.raises(InvalidStateError):
        await repo.pay_sale(sale.id, 10)


@pytest.mark.asyncio
async def test_pay_sale_negative_cash(repo, session):
    sale = await seed_sale(session, status="PENDING")

    with pytest.raises(BadRequestError):
        await repo.pay_sale(sale.id, -10)


@pytest.mark.asyncio
async def test_pay_sale_insufficient_cash(repo, session):
    await seed_system(session)
    sale = await seed_sale(session)
    product = await seed_product(session, barcode="X", price=10)

    await repo.add_product_to_sale(sale.id, product.barcode, 2)
    await repo.close_sale(sale.id)

    with pytest.raises(BadRequestError):
        await repo.pay_sale(sale.id, cash_amount=5)

@pytest.mark.asyncio
async def test_delete_sale_reintegrates_stock(repo, session):
    sale = await seed_sale(session, status="OPEN")

    product = await seed_product(
        session,
        barcode="P-DEL",
        quantity=10
    )

    await repo.add_product_to_sale(sale.id, product.barcode, 4)

    updated_product = await session.get(ProductTypeDAO, product.id)
    assert updated_product.quantity == 6

    result = await repo.delete_sale(sale.id)

    assert result is True

    restored_product = await session.get(ProductTypeDAO, product.id)
    assert restored_product.quantity == 10

    assert await repo.get_sale_by_id(sale.id) is None
