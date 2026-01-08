import pytest
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.repositories.return_repository import ReturnRepository
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.saleTransaction_dao import SaleTransactionDAO
from app.models.DAO.sale_product_association import SaleProductAssociation
from app.models.DAO.system_dao import SystemInfoDAO
from app.models.order_status import OrderStatus
from app.models.errors.bad_request import BadRequestError
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.invalid_state_error import InvalidStateError


# ---------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------

@pytest.fixture
async def session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def repo(session) -> ReturnRepository:
    return ReturnRepository(session)


@pytest.fixture(autouse=True)
async def clean_db():
    from app.database import database
    await database.reset_db()
    await database.init_db()


# ---------------------------------------------------------------------
# SEED HELPERS (CANONICAL)
# ---------------------------------------------------------------------

async def seed_product(session, *, barcode: str, quantity: int):
    product = ProductTypeDAO(
        barcode=barcode,
        description=f"Product {barcode}",
        price_per_unit=10.0,
        quantity=quantity,
        discountRate=0.0,
        note=None,
        shop_id=1,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def seed_paid_sale(session, product: ProductTypeDAO, quantity: int):
    sale = SaleTransactionDAO(
        status="PAID",
        discountRate=0.0,
        cost=quantity * product.price_per_unit,
        paymentType="CASH",
        closed_at=datetime.utcnow(),
    )
    session.add(sale)
    await session.flush()

    line = SaleProductAssociation(
        sale_transaction_id=sale.id,
        product_type_id=product.id,
        product_barcode=product.barcode,
        quantity=quantity,
        unit_price=product.price_per_unit,
        discount_rate=0.0,
    )
    session.add(line)

    product.quantity -= quantity

    sys = SystemInfoDAO(balance=1000.0)
    session.add(sys)

    await session.commit()
    await session.refresh(sale)
    return sale


# =====================================================================
# TESTS
# =====================================================================

@pytest.mark.asyncio
async def test_create_return(repo, session):
    product = await seed_product(session, barcode="P-RET", quantity=5)
    sale = await seed_paid_sale(session, product, quantity=2)

    ret = await repo.create_return(sale.id)

    assert ret.status == "OPEN"
    assert ret.sale_transaction_id == sale.id
    assert ret.product_lines == []


@pytest.mark.asyncio
async def test_add_product_to_return(repo, session):
    product = await seed_product(session, barcode="P-ADD", quantity=5)
    sale = await seed_paid_sale(session, product, quantity=2)

    ret = await repo.create_return(sale.id)

    await repo.add_product_to_return(ret.id, product.barcode, 1)

    # 🔴 RELOAD
    ret = await repo.get_return_by_id(ret.id)

    assert len(ret.product_lines) == 1
    assert ret.product_lines[0].quantity == 1


@pytest.mark.asyncio
async def test_add_product_exceeds_sold_quantity(repo, session):
    product = await seed_product(session, barcode="P-EX", quantity=5)
    sale = await seed_paid_sale(session, product, quantity=1)

    ret = await repo.create_return(sale.id)

    with pytest.raises(BadRequestError):
        await repo.add_product_to_return(
            return_id=ret.id,
            barcode=product.barcode,
            amount=2,
        )


@pytest.mark.asyncio
async def test_remove_product_from_return(repo, session):
    product = await seed_product(session, barcode="P-RM", quantity=5)
    sale = await seed_paid_sale(session, product, quantity=2)

    ret = await repo.create_return(sale.id)
    await repo.add_product_to_return(ret.id, product.barcode, 2)

    # 🔴 RELOAD BEFORE REMOVE ASSERTIONS
    ret = await repo.get_return_by_id(ret.id)
    assert len(ret.product_lines) == 1

    await repo.remove_product_from_return(ret.id, product.barcode, 1)

    # 🔴 RELOAD AGAIN
    ret = await repo.get_return_by_id(ret.id)
    assert ret.product_lines[0].quantity == 1


@pytest.mark.asyncio
async def test_close_return(repo, session):
    product = await seed_product(session, barcode="P-CLOSE", quantity=5)
    sale = await seed_paid_sale(session, product, quantity=2)

    ret = await repo.create_return(sale.id)
    await repo.add_product_to_return(ret.id, product.barcode, 2)

    # 🔴 RELOAD BEFORE CLOSE
    ret = await repo.get_return_by_id(ret.id)

    await repo.close_return(ret.id)

    # 🔴 RELOAD PRODUCT AFTER CLOSE
    refreshed_product = await session.get(ProductTypeDAO, product.id)
    assert refreshed_product.quantity == 5

    ret = await repo.get_return_by_id(ret.id)
    assert ret.status == "CLOSED"


@pytest.mark.asyncio
async def test_reimburse_return(repo, session):
    product = await seed_product(session, barcode="P-REF", quantity=5)
    sale = await seed_paid_sale(session, product, quantity=2)

    ret = await repo.create_return(sale.id)
    await repo.add_product_to_return(ret.id, product.barcode, 2)
    await repo.close_return(ret.id)

    result = await repo.reimburse_return(ret.id)

    assert result["refund_amount"] == 20.0

    ret = await repo.get_return_by_id(ret.id)
    assert ret.status == "REIMBURSED"


@pytest.mark.asyncio
async def test_delete_reimbursed_return_not_allowed(repo, session):
    product = await seed_product(session, barcode="P-DEL", quantity=5)
    sale = await seed_paid_sale(session, product, quantity=1)

    ret = await repo.create_return(sale.id)
    await repo.add_product_to_return(ret.id, product.barcode, 1)
    await repo.close_return(ret.id)
    await repo.reimburse_return(ret.id)

    with pytest.raises(InvalidStateError):
        await repo.delete_return(ret.id)
