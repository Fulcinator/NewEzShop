import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.repositories.product_type_repository import ProductTypeRepository
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.position_dao import PositionDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError


# ---------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------

@pytest.fixture
async def session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def repo(session) -> ProductTypeRepository:
    return ProductTypeRepository(session)


@pytest.fixture(autouse=True)
async def reset_db():
    from app.database import database
    await database.reset_db()
    await database.init_db()


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

class DummyCreateDTO:
    def __init__(
        self,
        *,
        barcode="P-1",
        description="Test product",
        price_per_unit=10.0,
        quantity=5,
        discountRate=None,
        note=None,
        position="1-A-1",
    ):
        self.barcode = barcode
        self.description = description
        self.price_per_unit = price_per_unit
        self.quantity = quantity
        self.discountRate = discountRate
        self.note = note
        self.position = position


# =====================================================================
# TESTS
# =====================================================================

@pytest.mark.asyncio
async def test_create_product_type_success(repo):
    dto = DummyCreateDTO()

    product = await repo.create_product_type(dto)

    assert product.id is not None
    assert product.barcode == "P-1"
    assert product.quantity == 5
    assert product.position is not None
    assert product.position.aisleID == 1
    assert product.position.rackID == "A"
    assert product.position.levelID == 1


@pytest.mark.asyncio
async def test_create_product_type_duplicate_barcode(repo):
    dto = DummyCreateDTO(barcode="DUP")

    await repo.create_product_type(dto)

    with pytest.raises(ConflictError):
        await repo.create_product_type(
            DummyCreateDTO(barcode="DUP", description="Other")
        )


@pytest.mark.asyncio
async def test_create_product_type_invalid_position_format(repo):
    dto = DummyCreateDTO(position="INVALID")

    with pytest.raises(ConflictError):
        await repo.create_product_type(dto)


@pytest.mark.asyncio
async def test_create_product_type_position_occupied(repo):
    await repo.create_product_type(DummyCreateDTO(position="1-A-1"))

    with pytest.raises(ConflictError):
        await repo.create_product_type(
            DummyCreateDTO(barcode="P-2", description="Second", position="1-A-1")
        )


@pytest.mark.asyncio
async def test_get_product_type_by_id(repo):
    created = await repo.create_product_type(DummyCreateDTO())

    fetched = await repo.get_product_type_by_id(created.id)

    assert fetched.id == created.id
    assert fetched.position is not None


@pytest.mark.asyncio
async def test_get_product_type_by_id_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.get_product_type_by_id(999)


@pytest.mark.asyncio
async def test_get_product_type_by_barcode(repo):
    await repo.create_product_type(DummyCreateDTO(barcode="BCODE"))

    fetched = await repo.get_product_type_by_barcode("BCODE")

    assert fetched.barcode == "BCODE"


@pytest.mark.asyncio
async def test_get_product_type_by_barcode_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.get_product_type_by_barcode("UNKNOWN")


@pytest.mark.asyncio
async def test_list_product_types(repo):
    await repo.create_product_type(DummyCreateDTO(barcode="P1"))
    await repo.create_product_type(
        DummyCreateDTO(barcode="P2", position="1-A-2", description="Second")
    )

    products = await repo.list_product_types()

    assert len(products) == 2


@pytest.mark.asyncio
async def test_search_product_types_by_description(repo):
    await repo.create_product_type(DummyCreateDTO(description="Apple Juice"))
    await repo.create_product_type(
        DummyCreateDTO(
            barcode="P2",
            description="Orange Juice",
            position="1-A-2",
        )
    )

    result = await repo.search_product_types(description="Apple")

    assert len(result) == 1
    assert result[0].description == "Apple Juice"


@pytest.mark.asyncio
async def test_patch_quantity_success(repo):
    product = await repo.create_product_type(DummyCreateDTO())

    await repo.patch_quantity(product.id, 20)

    updated = await repo.get_product_type_by_id(product.id)
    assert updated.quantity == 20


@pytest.mark.asyncio
async def test_patch_quantity_negative(repo):
    product = await repo.create_product_type(DummyCreateDTO())

    with pytest.raises(ConflictError):
        await repo.patch_quantity(product.id, -1)


@pytest.mark.asyncio
async def test_patch_position_success(repo):
    product = await repo.create_product_type(DummyCreateDTO())

    await repo.patch_position(product.id, "1-B-3")

    updated = await repo.get_product_type_by_id(product.id)
    assert updated.position.rackID == "B"
    assert updated.position.levelID == 3


@pytest.mark.asyncio
async def test_patch_position_remove(repo):
    product = await repo.create_product_type(DummyCreateDTO())

    await repo.patch_position(product.id, None)

    updated = await repo.get_product_type_by_id(product.id)
    assert updated.position is None


@pytest.mark.asyncio
async def test_delete_product_type(repo):
    product = await repo.create_product_type(DummyCreateDTO())

    await repo.delete_product_type(product.id)

    with pytest.raises(NotFoundError):
        await repo.get_product_type_by_id(product.id)

@pytest.mark.asyncio
async def test_update_product_type_updates_fields_and_position(repo):
    # create initial
    created = await repo.create_product_type(
        DummyCreateDTO(
            barcode="UPD-1",
            description="Old desc",
            price_per_unit=10.0,
            quantity=5,
            position="1-A-1",
        )
    )

    # fake Pydantic-like update dto
    class DummyUpdateDTO:
        def model_dump(self, exclude_unset=True):
            return {
                "description": "New desc",
                "price_per_unit": 99.0,
                "quantity": 50,
                "position": "2-B-3",
            }

    updated = await repo.update_product_type(created.id, DummyUpdateDTO())

    assert updated.id == created.id
    assert updated.description == "New desc"
    assert updated.price_per_unit == 99.0
    assert updated.quantity == 50

    # position updated
    assert updated.position is not None
    assert updated.position.aisleID == 2
    assert updated.position.rackID == "B"
    assert updated.position.levelID == 3


@pytest.mark.asyncio
async def test_update_product_type_remove_position(repo):
    created = await repo.create_product_type(
        DummyCreateDTO(
            barcode="UPD-2",
            description="Has pos",
            position="1-A-1",
        )
    )

    class DummyUpdateDTO:
        def model_dump(self, exclude_unset=True):
            return {"position": None}

    updated = await repo.update_product_type(created.id, DummyUpdateDTO())


    reloaded = await repo.get_product_type_by_id(updated.id)

    assert reloaded.position is None
    assert reloaded.position_id is None



@pytest.mark.asyncio
async def test_update_product_type_fails_if_new_position_occupied(repo):
    # product 1 in 1-A-1
    p1 = await repo.create_product_type(
        DummyCreateDTO(barcode="UPD-3", description="P1", position="1-A-1")
    )
    # product 2 in 1-A-2
    p2 = await repo.create_product_type(
        DummyCreateDTO(barcode="UPD-4", description="P2", position="1-A-2")
    )

    class DummyUpdateDTO:
        def model_dump(self, exclude_unset=True):
            return {"position": "1-A-1"}  # occupied by p1

    with pytest.raises(ConflictError):
        await repo.update_product_type(p2.id, DummyUpdateDTO())


@pytest.mark.asyncio
async def test_update_product_type_not_found(repo):
    class DummyUpdateDTO:
        def model_dump(self, exclude_unset=True):
            return {"description": "Doesn't matter"}

    with pytest.raises(NotFoundError):
        await repo.update_product_type(9999, DummyUpdateDTO())


@pytest.mark.asyncio
async def test_update_product_type_invalid_position_format(repo):
    created = await repo.create_product_type(
        DummyCreateDTO(barcode="UPD-5", description="P", position="1-A-1")
    )

    class DummyUpdateDTO:
        def model_dump(self, exclude_unset=True):
            return {"position": "BADFORMAT"}

    with pytest.raises(ConflictError):
        await repo.update_product_type(created.id, DummyUpdateDTO())
