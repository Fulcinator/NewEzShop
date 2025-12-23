import pytest
from app.controllers.inventory_controller import InventoryController
from tests.unit.fakes.fake_inventory_repo import FakeInventoryRepository
from app.models.DTO.inventory_dto import QuantityUpdateDTO
from app.models.DTO.position_dto import PositionDTO


@pytest.mark.asyncio
async def test_update_quantity_success():
    repo = FakeInventoryRepository()
    controller = InventoryController()
    controller.repo = repo  # inject fake repo

    dto = QuantityUpdateDTO(new_quantity=20)

    result = await controller.update_quantity(1, dto)

    assert result.quantity == 20
    assert repo.items[1].quantity == 20


@pytest.mark.asyncio
async def test_update_quantity_invalid_id():
    repo = FakeInventoryRepository()
    controller = InventoryController()
    controller.repo = repo

    dto = QuantityUpdateDTO(new_quantity=15)

    with pytest.raises(ValueError):
        await controller.update_quantity(999, dto)


@pytest.mark.asyncio
async def test_update_position_success():
    repo = FakeInventoryRepository()
    controller = InventoryController()
    controller.repo = repo

    dto = PositionDTO(aisleID=1, rackID=2, levelID=3)

    result = await controller.update_position(1, dto)

    assert result.position_id is None
    assert repo.items[1].position.aisleID == 1
    assert repo.items[1].position.rackID == 2
    assert repo.items[1].position.levelID == 3


@pytest.mark.asyncio
async def test_update_position_invalid_id():
    repo = FakeInventoryRepository()
    controller = InventoryController()
    controller.repo = repo

    dto = PositionDTO(aisleID=1, rackID=2, levelID=3)

    with pytest.raises(ValueError):
        await controller.update_position(999, dto)