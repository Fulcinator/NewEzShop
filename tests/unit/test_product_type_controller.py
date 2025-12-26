import pytest
from app.controllers.product_type_controller import ProductTypeController
from app.models.DTO.product_type_dto import (
    ProductTypeCreateDTO,
    ProductTypeUpdateDTO,
)
from tests.unit.fakes.fake_product_type import (FakeProductTypeRepository,FakeProductTypeDAO)


@pytest.mark.asyncio
async def test_create_product_type_success(monkeypatch):
    controller = ProductTypeController()
    fake_repo = FakeProductTypeRepository()

    monkeypatch.setattr(controller, "repo", fake_repo)

    dto = ProductTypeCreateDTO(
        barcode="123",
        name="Milk",
        sellPrice=1.5,
        quantity=10,
    )

    result = await controller.create(dto)

    assert result.id == 1
    assert result.barcode == "123"
    assert result.name == "Milk"
    assert result.sellPrice == 1.5
    assert result.quantity == 10

@pytest.mark.asyncio
async def test_update_product_type_success(monkeypatch):
    controller = ProductTypeController()
    fake_repo = FakeProductTypeRepository()

    # pre-create
    fake_repo.product = FakeProductTypeDAO()

    monkeypatch.setattr(controller, "repo", fake_repo)

    dto = ProductTypeUpdateDTO(
        name="Updated Milk",
        sellPrice=2.0,
        quantity=20,
    )

    result = await controller.update(1, dto)

    assert result.name == "Updated Milk"
    assert result.sellPrice == 2.0
    assert result.quantity == 20

@pytest.mark.asyncio
async def test_delete_product_type(monkeypatch):
    controller = ProductTypeController()
    fake_repo = FakeProductTypeRepository()

    fake_repo.product = FakeProductTypeDAO()

    monkeypatch.setattr(controller, "repo", fake_repo)

    result = await controller.delete(1)

    assert result is True
    assert fake_repo.product is None

@pytest.mark.asyncio
async def test_list_all_products(monkeypatch):
    controller = ProductTypeController()
    fake_repo = FakeProductTypeRepository()

    fake_repo.product = FakeProductTypeDAO()

    monkeypatch.setattr(controller, "repo", fake_repo)

    results = await controller.list_all()

    assert len(results) == 1
    assert results[0].barcode == "123"

@pytest.mark.asyncio
async def test_search_product_by_barcode(monkeypatch):
    controller = ProductTypeController()
    fake_repo = FakeProductTypeRepository()

    fake_repo.product = FakeProductTypeDAO(barcode="999")

    monkeypatch.setattr(controller, "repo", fake_repo)

    results = await controller.search(barcode="999")

    assert len(results) == 1
    assert results[0].barcode == "999"

@pytest.mark.asyncio
async def test_search_product_not_found(monkeypatch):
    controller = ProductTypeController()
    fake_repo = FakeProductTypeRepository()

    fake_repo.product = FakeProductTypeDAO(barcode="123")

    monkeypatch.setattr(controller, "repo", fake_repo)

    results = await controller.search(barcode="000")

    assert results == []
