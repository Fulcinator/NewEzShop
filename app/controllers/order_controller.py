from datetime import datetime
from typing import List, Optional
from app.repositories.order_repository import OrderRepository
from app.models.DTO.order_dto import OrderCreateDTO, OrderResponseDTO
from app.models.order_status import OrderStatus
from app.services.mapper_service import orderDao_toDto

class OrderController:
    def __init__(self):
        self.repo = OrderRepository()

    def _to_response_dto(self, order) -> OrderResponseDTO:
        product_type = order.product_types[0] if order.product_types else None
        product_barcode = product_type.barcode if product_type else None

        return OrderResponseDTO(
            id=order.id,
            product_barcode=product_barcode,
            quantity=order.quantity,
            price_per_unit=order.price_per_unit,
            status=order.status,
            issue_date=order.issue_date,
        )

    async def issue_reorder(self, dto: OrderCreateDTO) -> OrderResponseDTO:
        order = await self.repo.issue_reorder_warning(
            dto.product_barcode,
            dto.quantity,
            dto.price_per_unit,
        )
        return self._to_response_dto(order)

    async def pay_for_order(self, dto: OrderCreateDTO) -> OrderResponseDTO:
        order = await self.repo.create_and_pay_order(
            dto.product_barcode,
            dto.quantity,
            dto.price_per_unit
        )
        return self._to_response_dto(order)
    
    async def pay_order(self, order_id: int):
        await self.repo.pay_issued_and_update_balance(order_id)
        return {"success": True}

    async def record_arrival(self, order_id: int):
        await self.repo.record_arrival_and_update_quantity(order_id)
        return {"success": True}
        
    async def list_orders(self, status: Optional[OrderStatus]) -> List[OrderResponseDTO]:
        orders = await self.repo.list_orders(status)
        return [orderDao_toDto(o) for o in orders]
    
""" not used anymore
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
"""
