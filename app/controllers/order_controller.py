from typing import List, Optional
from app.repositories.order_repository import OrderRepository
from app.models.DTO.order_dto import OrderCreateDTO, OrderResponseDTO
from app.models.order_status import OrderStatus

class OrderController:
    def __init__(self):
        self.repo = OrderRepository()

    def _to_response_dto(self, order) -> OrderResponseDTO:
        product_type_id = order.product_types[0].id if order.product_types else None
        return OrderResponseDTO(
            id=order.id,
            product_type_id=product_type_id,
            supplier=order.supplier,
            status=order.status,
            quantity=order.quantity,
            price_per_unit=order.price_per_unit
        )

    async def issue_reorder(self, dto: OrderCreateDTO) -> OrderResponseDTO:
        order = await self.repo.issue_reorder_warning(
            dto.product_type_id, dto.supplier, dto.quantity, dto.price_per_unit
        )
        return self._to_response_dto(order)

    async def send_and_pay(self, dto: OrderCreateDTO) -> OrderResponseDTO:
        order = await self.repo.send_and_pay_order(
            dto.product_type_id, dto.supplier, dto.quantity, dto.price_per_unit
        )
        return self._to_response_dto(order)

    async def pay_issued(self, order_id: int) -> OrderResponseDTO:
        order = await self.repo.pay_issued_order(order_id)
        return self._to_response_dto(order)

    async def record_arrival(self, order_id: int) -> OrderResponseDTO:
        order = await self.repo.record_arrival(order_id)
        return self._to_response_dto(order)

    async def list_orders(self, status: Optional[OrderStatus]) -> List[OrderResponseDTO]:
        orders = await self.repo.list_orders(status)
        return [self._to_response_dto(o) for o in orders]
