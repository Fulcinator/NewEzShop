import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.repositories.loyalty_card_repository import LoyaltyCardRepository
from app.models.DAO.loyaltyCard_dao import LoyaltyCardDAO
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
async def repo(session) -> LoyaltyCardRepository:
    return LoyaltyCardRepository(session)


@pytest.fixture(autouse=True)
async def clean_db():
    from app.database import database
    await database.reset_db()
    await database.init_db()


# simple DTO-like object
class DummyData:
    def __init__(self, card_id: str, points: int = 0):
        self.card_id = card_id
        self.points = points


async def seed_card(session, card_id: str, points: int = 0):
    card = LoyaltyCardDAO(
        card_id=str(card_id).zfill(10),
        points=points
    )
    session.add(card)
    await session.commit()
    return card


# =====================================================================
# TESTS
# =====================================================================

@pytest.mark.asyncio
async def test_create_loyalty_card_success(repo):
    data = DummyData(card_id="123", points=10)

    card = await repo.create_loyalty_card(data)

    assert card.card_id == "123"
    assert card.points == 10


@pytest.mark.asyncio
async def test_create_loyalty_card_conflict(repo, session):
    await seed_card(session, card_id="0000000123")

    data = DummyData(card_id="0000000123", points=5)

    with pytest.raises(ConflictError):
        await repo.create_loyalty_card(data)


@pytest.mark.asyncio
async def test_attach_loyalty_card_to_customer_success(repo, session):
    card = await seed_card(session, card_id="0000009999")

    # minimal customer
    from app.models.DAO.customer_dao import CustomerDAO
    customer = CustomerDAO(name="Test Customer")
    session.add(customer)
    await session.commit()

    updated = await repo.attach_loyalty_card_to_customer(
        loyalty_card_id="9999",
        customer_id=customer.id
    )

    assert updated.customer_id == customer.id


@pytest.mark.asyncio
async def test_attach_loyalty_card_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.attach_loyalty_card_to_customer("0000000001", 1)


@pytest.mark.asyncio
async def test_add_points_success(repo, session):
    card = await seed_card(session, card_id="0000001111", points=5)

    updated = await repo.add_points(card.card_id, 10)

    assert updated.points == 15


@pytest.mark.asyncio
async def test_add_points_cannot_go_negative(repo, session):
    card = await seed_card(session, card_id="0000002222", points=5)

    updated = await repo.add_points(card.card_id, -100)

    assert updated.points == 0


@pytest.mark.asyncio
async def test_add_points_card_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.add_points("0000000000", 10)


@pytest.mark.asyncio
async def test_delete_card_success(repo, session):
    card = await seed_card(session, card_id="0000003333")

    await repo.delete_card(card.card_id)

    result = await session.get(LoyaltyCardDAO, card.id)
    assert result is None


@pytest.mark.asyncio
async def test_delete_card_not_existing(repo):
    # should NOT raise
    await repo.delete_card("0000009999")


@pytest.mark.asyncio
async def test_update_card_success(repo, session):
    card = await seed_card(session, card_id="0000004444", points=10)

    updated = await repo.update_card(
        old_card_id=card.card_id,
        new_card_id="0000005555",
        points=20
    )

    assert updated.card_id == "0000005555"
    assert updated.points == 20


@pytest.mark.asyncio
async def test_update_card_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.update_card(
            old_card_id="0000000000",
            new_card_id="0000000001",
            points=5
        )


@pytest.mark.asyncio
async def test_create_loyalty_card_and_attach(repo, session):
    from app.models.DAO.customer_dao import CustomerDAO

    customer = CustomerDAO(name="Attach Test")
    session.add(customer)
    await session.commit()

    card = await repo.create_loyalty_card_and_attach(
        customer_id=customer.id,
        card_id="0000007777",
        points=30
    )

    assert card.customer_id == customer.id
    assert card.points == 30
