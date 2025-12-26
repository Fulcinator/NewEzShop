import pytest
from unittest.mock import AsyncMock

from app.controllers.order_controller import OrderController
from app.models.DTO.order_dto import OrderCreateDTO
from app.models.order_status import OrderStatus


# ---------- Fake domain objects ----------

class FakeProductType:
    def __init__(self, id: int):
        self.id = id


class FakeOrder:
    def __init__(
        self,
        id=1,
        product_type_id=10,
        supplier="ACME",
        status=OrderStatus.ISSUED,
        quantity=5,
        price_per_unit=100.0
    ):
        self.id = id
        self.supplier = supplier
        self.status = status
        self.quantity = quantity
        self.price_per_unit = price_per_unit
        self.product_types = [FakeProductType(product_type_id)]



@pytest.fixture
def controller():
    controller = OrderController()
    controller.repo = AsyncMock()
    return controller


@pytest.fixture
def order_dto():
    return OrderCreateDTO(
        product_type_id=10,
        supplier="ACME",
        quantity=5,
        price_per_unit=100.0
    )



@pytest.mark.asyncio
async def test_issue_reorder_success(controller, order_dto):
    fake_order = FakeOrder(status=OrderStatus.ISSUED)
    controller.repo.issue_reorder_warning.return_value = fake_order

    result = await controller.issue_reorder(order_dto)

    controller.repo.issue_reorder_warning.assert_awaited_once_with(
        order_dto.product_type_id,
        order_dto.supplier,
        order_dto.quantity,
        order_dto.price_per_unit
    )

    assert result.id == fake_order.id
    assert result.product_type_id == 10
    assert result.status == OrderStatus.ISSUED


@pytest.mark.asyncio
async def test_send_and_pay_success(controller, order_dto):
    fake_order = FakeOrder(status=OrderStatus.PAYED)
    controller.repo.send_and_pay_order.return_value = fake_order

    result = await controller.send_and_pay(order_dto)

    controller.repo.send_and_pay_order.assert_awaited_once()
    assert result.status == OrderStatus.PAYED


@pytest.mark.asyncio
async def test_pay_issued_success(controller):
    fake_order = FakeOrder(status=OrderStatus.PAYED)
    controller.repo.pay_issued_order.return_value = fake_order

    result = await controller.pay_issued(order_id=1)

    controller.repo.pay_issued_order.assert_awaited_once_with(1)
    assert result.status == OrderStatus.PAYED


@pytest.mark.asyncio
async def test_record_arrival_success(controller):
    fake_order = FakeOrder(status=OrderStatus.COMPLETED)
    controller.repo.record_arrival.return_value = fake_order

    result = await controller.record_arrival(order_id=1)

    controller.repo.record_arrival.assert_awaited_once_with(1)
    assert result.status == OrderStatus.COMPLETED


@pytest.mark.asyncio
async def test_list_orders_with_status(controller):
    fake_orders = [
        FakeOrder(id=1),
        FakeOrder(id=2),
    ]
    controller.repo.list_orders.return_value = fake_orders

    result = await controller.list_orders(status=OrderStatus.ISSUED)

    controller.repo.list_orders.assert_awaited_once_with(OrderStatus.ISSUED)
    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2


@pytest.mark.asyncio
async def test_list_orders_without_status(controller):
    controller.repo.list_orders.return_value = []

    result = await controller.list_orders(status=None)

    controller.repo.list_orders.assert_awaited_once_with(None)
    assert result == []
