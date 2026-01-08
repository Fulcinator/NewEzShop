import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import AsyncSessionLocal
from app.repositories.inventory_repository import InventoryRepository
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.position_dao import PositionDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError


# ---------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------

@pytest.fixture
async def session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def repo(session) -> InventoryRepository:
    return InventoryRepository(session)


@pytest.fixture(autouse=True)
async def clean_db():
    from app.database import database
    await database.reset_db()
    await database.init_db()


async def seed_product_type(
    session,
    *,
    barcode: str,
    quantity: int = 10,
    with_position: bool = False,
):
    pt = ProductTypeDAO(
        barcode=barcode,
        description=f"Product {barcode}",
        price_per_unit=10.0,
        quantity=quantity,
        shop_id=1,
    )
    session.add(pt)
    await session.flush()

    if with_position:
        pos = PositionDAO(
            aisleID=1,
            rackID=1,
            levelID=1,
        )
        session.add(pos)
        await session.flush()
        pt.position = pos

    await session.commit()
    return pt


# =====================================================================
# TESTS: update_quantity
# =====================================================================

@pytest.mark.asyncio
async def test_update_quantity_success(repo, session):
    pt = await seed_product_type(session, barcode="P-QTY", quantity=5)

    updated = await repo.update_quantity(pt.id, 20)

    assert updated.quantity == 20


@pytest.mark.asyncio
async def test_update_quantity_zero_allowed(repo, session):
    pt = await seed_product_type(session, barcode="P-ZERO", quantity=5)

    updated = await repo.update_quantity(pt.id, 0)

    assert updated.quantity == 0


@pytest.mark.asyncio
async def test_update_quantity_negative_not_allowed(repo):
    with pytest.raises(BadRequestError):
        await repo.update_quantity(product_type_id=999, new_quantity=-1)


@pytest.mark.asyncio
async def test_update_quantity_product_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.update_quantity(product_type_id=999, new_quantity=10)


# =====================================================================
# TESTS: update_position
# =====================================================================



@pytest.mark.asyncio
async def test_update_position_creates_position(repo, session):
    pt = await seed_product_type(session, barcode="P-POS-NEW", with_position=False)

    await repo.update_position(
        product_type_id=pt.id,
        aisleID=2,
        rackID=3,
        levelID=4,
    )

    reloaded = await session.get(
        ProductTypeDAO,
        pt.id,
        options=[selectinload(ProductTypeDAO.position)]
    )

    assert reloaded.position is not None
    assert reloaded.position.aisleID == 2
    assert reloaded.position.rackID == "3"   
    assert reloaded.position.levelID == 4


@pytest.mark.asyncio
async def test_update_position_updates_existing_position(repo, session):
    pt = await seed_product_type(session, barcode="P-POS-UPD", with_position=True)

    await repo.update_position(
        product_type_id=pt.id,
        aisleID=5,
        rackID=6,
        levelID=7,
    )

    reloaded = await session.get(
        ProductTypeDAO,
        pt.id,
        options=[selectinload(ProductTypeDAO.position)]
    )

    assert reloaded.position is not None
    assert reloaded.position.aisleID == 5
    assert reloaded.position.rackID == "6"   
    assert reloaded.position.levelID == 7




@pytest.mark.asyncio
async def test_update_position_product_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.update_position(
            product_type_id=999,
            aisleID=1,
            rackID=1,
            levelID=1,
        )
