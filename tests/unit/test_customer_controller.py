import pytest
from app.controllers.customer_controller import CustomerController
from tests.unit.fakes.fake_customer_repo import FakeCustomerRepository
from tests.unit.fakes.fake_loyalty_card_repo import FakeLoyaltyCardRepository
from app.models.DTO.customer_dto import CustomerCreateDTO, CustomerUpdateDTO


@pytest.mark.asyncio
async def test_create_customer():
    controller = CustomerController()
    controller.customer_repo = FakeCustomerRepository()
    controller.loyalty_card_repo = FakeLoyaltyCardRepository()

    dto = CustomerCreateDTO(name="Mario", surname="Rossi")
    result = await controller.create_customer(dto)

    assert result.name == "Mario"
    assert result.surname == "Rossi"


@pytest.mark.asyncio
async def test_get_customer_by_id():
    controller = CustomerController()
    controller.customer_repo = FakeCustomerRepository()
    controller.loyalty_card_repo = FakeLoyaltyCardRepository()

    dto = CustomerCreateDTO(name="Luca", surname="Bianchi")
    created = await controller.create_customer(dto)

    fetched = await controller.get_customer_by_id(created.id)

    assert fetched.id == created.id
    assert fetched.name == "Luca"


@pytest.mark.asyncio
async def test_update_customer():
    controller = CustomerController()
    controller.customer_repo = FakeCustomerRepository()
    controller.loyalty_card_repo = FakeLoyaltyCardRepository()

    created = await controller.create_customer(
        CustomerCreateDTO(name="Anna", surname="Verdi")
    )

    updated = await controller.update_customer(
        created.id,
        CustomerUpdateDTO(name="Anna Maria", surname=None)
    )

    assert updated.name == "Anna Maria"
    assert updated.surname == "Verdi"


@pytest.mark.asyncio
async def test_attach_loyalty_card():
    controller = CustomerController()
    controller.customer_repo = FakeCustomerRepository()
    controller.loyalty_card_repo = FakeLoyaltyCardRepository()

    created = await controller.create_customer(
        CustomerCreateDTO(name="Paolo", surname="Neri")
    )

    updated = await controller.attach_loyalty_card_to_customer(
        created.id, 1
    )

    assert updated.id == created.id
    assert controller.loyalty_card_repo.cards[1].customer_id == created.id