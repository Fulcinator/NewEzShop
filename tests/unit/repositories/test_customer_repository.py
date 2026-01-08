import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.repositories.customer_repository import CustomerRepository
from app.models.DAO.customer_dao import CustomerDAO
from app.models.DAO.loyaltyCard_dao import LoyaltyCardDAO
from app.models.DTO.customer_dto import CustomerUpdateDTO
from app.models.DTO.loyalty_card_dto import LoyaltyCardUpdateDTO
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
async def repo(session) -> CustomerRepository:
    return CustomerRepository(session)


@pytest.fixture(autouse=True)
async def clean_db():
    from app.database import database
    await database.reset_db()
    await database.init_db()


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

async def seed_customer(session, *, name: str) -> CustomerDAO:
    customer = CustomerDAO(name=name)
    session.add(customer)
    await session.commit()
    return customer


async def seed_customer_with_card(
    session,
    *,
    name: str,
    card_id="0000000001",
    points=10
) -> CustomerDAO:
    customer = CustomerDAO(name=name)
    session.add(customer)
    await session.flush()

    card = LoyaltyCardDAO(
        card_id=card_id,
        points=points,
        customer_id=customer.id
    )
    session.add(card)
    await session.commit()

    return customer


# =====================================================================
# TESTS
# =====================================================================

@pytest.mark.asyncio
async def test_create_customer_success(repo):
    dto = type("DTO", (), {"name": "Alice"})()

    customer = await repo.create_customer(dto)

    assert customer.id is not None
    assert customer.name == "Alice"
    assert customer.loyalty_card is None


@pytest.mark.asyncio
async def test_create_customer_conflict(repo):
    dto = type("DTO", (), {"name": "Bob"})()
    await repo.create_customer(dto)

    with pytest.raises(ConflictError):
        await repo.create_customer(dto)


@pytest.mark.asyncio
async def test_get_customer_by_id_success(repo, session):
    customer = await seed_customer(session, name="Charlie")

    fetched = await repo.get_customer_by_id(customer.id)

    assert fetched.id == customer.id
    assert fetched.name == "Charlie"


@pytest.mark.asyncio
async def test_get_customer_by_id_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.get_customer_by_id(999)


@pytest.mark.asyncio
async def test_list_customers(repo, session):
    await seed_customer(session, name="A")
    await seed_customer(session, name="B")

    customers = await repo.list_customers()

    assert len(customers) >= 2


@pytest.mark.asyncio
async def test_search_customers_by_name(repo, session):
    await seed_customer(session, name="John Doe")
    await seed_customer(session, name="Jane Smith")

    results = await repo.search_customers(name="john")

    assert len(results) == 1
    assert results[0].name == "John Doe"


@pytest.mark.asyncio
async def test_update_customer_name_only(repo, session):
    customer = await seed_customer(session, name="Old Name")

    dto = CustomerUpdateDTO(name="New Name")

    updated = await repo.update_customer(customer.id, dto)

    assert updated.name == "New Name"
    assert updated.loyalty_card is None


@pytest.mark.asyncio
async def test_update_customer_attach_loyalty_card(repo, session):
    customer = await seed_customer(session, name="Cardless")

    dto = CustomerUpdateDTO(
        card=LoyaltyCardUpdateDTO(
            card_id="0000000123",
            points=50
        )
    )

    updated = await repo.update_customer(customer.id, dto)

    assert updated.loyalty_card is not None
    assert updated.loyalty_card.card_id == "0000000123"
    assert updated.loyalty_card.points == 50


@pytest.mark.asyncio
async def test_update_customer_update_existing_card(repo, session):
    customer = await seed_customer_with_card(session, name="WithCard")

    dto = CustomerUpdateDTO(
        card=LoyaltyCardUpdateDTO(
            card_id="0000000999",
            points=100
        )
    )

    updated = await repo.update_customer(customer.id, dto)

    assert updated.loyalty_card.card_id == "0000000999"
    assert updated.loyalty_card.points == 100


@pytest.mark.asyncio
async def test_update_customer_detach_loyalty_card(repo, session):
    customer = await seed_customer_with_card(session, name="DetachMe")

    dto = CustomerUpdateDTO(card=None)

    updated = await repo.update_customer(customer.id, dto)

    assert updated.loyalty_card is None


@pytest.mark.asyncio
async def test_update_customer_invalid_customer(repo):
    dto = CustomerUpdateDTO(name="X")

    with pytest.raises(NotFoundError):
        await repo.update_customer(999, dto)


@pytest.mark.asyncio
async def test_delete_customer_success(repo, session):
    customer = await seed_customer(session, name="ToDelete")

    await repo.delete_customer(customer.id)

    with pytest.raises(NotFoundError):
        await repo.get_customer_by_id(customer.id)


@pytest.mark.asyncio
async def test_delete_customer_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.delete_customer(999)
