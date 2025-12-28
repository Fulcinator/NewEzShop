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

@pytest.mark.asyncio
async def test_search_customers_by_name():
    controller = CustomerController()
    controller.customer_repo = FakeCustomerRepository()
    controller.loyalty_card_repo = FakeLoyaltyCardRepository()

    await controller.create_customer(
        CustomerCreateDTO(name="Anna", surname="Verdi")
    )
    await controller.create_customer(
        CustomerCreateDTO(name="Anna", surname="Bianchi")
    )
    await controller.create_customer(
        CustomerCreateDTO(name="Maria", surname="Rossi")
    )

    results = await controller.search_customers(name="Anna")

    assert len(results) == 2
    assert all(c.name == "Anna" for c in results)

@pytest.mark.asyncio
async def test_search_customers_by_surname():
    controller = CustomerController()
    controller.customer_repo = FakeCustomerRepository()
    controller.loyalty_card_repo = FakeLoyaltyCardRepository()

    await controller.create_customer(
        CustomerCreateDTO(name="Anna", surname="Verdi")
    )
    await controller.create_customer(
        CustomerCreateDTO(name="Luca", surname="Verdi")
    )
    await controller.create_customer(
        CustomerCreateDTO(name="Paolo", surname="Neri")
    )

    results = await controller.search_customers(surname="Verdi")

    assert len(results) == 2
    assert all(c.surname == "Verdi" for c in results)

@pytest.mark.asyncio
async def test_list_customers_returns_all_customers():
    controller = CustomerController()
    controller.customer_repo = FakeCustomerRepository()
    controller.loyalty_card_repo = FakeLoyaltyCardRepository()

    # create customers
    await controller.create_customer(
        CustomerCreateDTO(name="Mario", surname="Rossi")
    )
    await controller.create_customer(
        CustomerCreateDTO(name="Luca", surname="Bianchi")
    )

    # list customers
    customers = await controller.list_customers()

    # assertions
    assert isinstance(customers, list)
    assert len(customers) == 2
    assert customers[0].name == "Mario"
    assert customers[1].name == "Luca"
