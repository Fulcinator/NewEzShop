import pytest
from types import SimpleNamespace
from app.controllers.loyalty_card_controller import LoyaltyCardController
from tests.unit.fakes.fake_loyalty_card_repo import FakeLoyaltyCardRepository
from app.models.DTO.loyalty_card_dto import LoyaltyCardCreateDTO


# ------------------------------------------------------------------
# PATCHED FAKE REPOSITORY
# ------------------------------------------------------------------

@pytest.fixture
def patched_repo():
    repo = FakeLoyaltyCardRepository()

    # Ensure storage exists
    if not hasattr(repo, "cards"):
        repo.cards = {}

    # ---- create_loyalty_card ----
    async def create_loyalty_card(dto):
        new_id = max(repo.cards.keys(), default=0) + 1
        card = SimpleNamespace(
            id=new_id,
            card_code=dto.card_code,
            points=dto.points or 0,
            customer_id=dto.customer_id
        )
        repo.cards[new_id] = card
        return card

    # ---- attach_loyalty_card_to_customer ----
    async def attach_loyalty_card_to_customer(card_id, customer_id):
        card = repo.cards[card_id]
        card.customer_id = customer_id
        return card

    # ---- add_points ----
    async def add_points(card_id, points):
        card = repo.cards[card_id]
        card.points += points
        return card

    repo.create_loyalty_card = create_loyalty_card
    repo.attach_loyalty_card_to_customer = attach_loyalty_card_to_customer
    repo.add_points = add_points

    return repo


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_loyalty_card(patched_repo):
    controller = LoyaltyCardController()
    controller.repo = patched_repo

    dto = LoyaltyCardCreateDTO(
        card_code="CARD000001",  # exactly 10 chars
        points=0
    )

    result = await controller.create_loyalty_card(dto)

    assert isinstance(result.id, int)
    assert result.card_code == "CARD000001"
    assert result.points == 0
    assert result.customer_id is None


@pytest.mark.asyncio
async def test_attach_loyalty_card_to_customer(patched_repo):
    controller = LoyaltyCardController()
    controller.repo = patched_repo

    card = await controller.create_loyalty_card(
        LoyaltyCardCreateDTO(
            card_code="CARD000002",
            points=10
        )
    )

    updated = await controller.attach_loyalty_card_to_customer(
        card_id=card.id,
        customer_id=42
    )

    assert updated.customer_id == 42
    assert patched_repo.cards[card.id].customer_id == 42


@pytest.mark.asyncio
async def test_add_points_to_loyalty_card(patched_repo):
    controller = LoyaltyCardController()
    controller.repo = patched_repo

    card = await controller.create_loyalty_card(
        LoyaltyCardCreateDTO(
            card_code="CARD000003",
            points=50
        )
    )

    updated = await controller.add_points(card.id, 25)

    assert updated.points == 75
    assert patched_repo.cards[card.id].points == 75
