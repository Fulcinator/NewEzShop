from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from app.config.config import ROUTES
from app.controllers.order_controller import OrderController
from app.models.DTO.order_dto import OrderCreateDTO, OrderResponseDTO
from app.models.order_status import OrderStatus
from app.middleware.auth_middleware import authenticate_user
from app.models.user_type import UserType

router = APIRouter(
    prefix=ROUTES["V1_ORDERS"],
    tags=["Orders"],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))]
)

controller = OrderController()

@router.post(
    "",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(body: OrderCreateDTO):
    """
    Creates a new order for a given product.
    The new order is in the ISSUED state.
    If an id is provided in the request, it will be ignored.
    """
    return await controller.issue_reorder(body)

@router.post(
    "/payfor",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED
)
async def pay_for_order(body: OrderCreateDTO):
    """
    Creates a new order and immediately pays for it.
    """
    return await controller.pay_for_order(body)

@router.patch("/{order_id}/pay")
async def pay_order(order_id: int):
    """
    Pays an existing ISSUED order.
    The order becomes PAYED and the balance is updated.
    """
    return await controller.pay_order(order_id)

@router.patch("/{order_id}/arrival")
async def record_arrival(order_id: int):
    """
    Marks a PAYED order as COMPLETED and updates product quantities.
    """
    return await controller.record_arrival(order_id)

@router.get("/", response_model=List[OrderResponseDTO])
async def list_orders(order_status: Optional[OrderStatus] = None):
    """
    List all orders (issued, payed, completed)
    """
    return await controller.list_orders(order_status)

"""not used anymore
@router.post("/reorder-warning", response_model=OrderResponseDTO, status_code=status.HTTP_201_CREATED)
async def issue_reorder_warning(body: OrderCreateDTO):
    
    Issue a reorder warning for a product type
    Creates an order in ISSUED state.
    
    return await controller.issue_reorder(body)

@router.post("/send-and-pay", response_model=OrderResponseDTO, status_code=status.HTTP_201_CREATED)
async def send_and_pay_order(body: OrderCreateDTO):
    
    Send and pay an order for a product type
    Creates an order directly in PAYED state.
    
    return await controller.send_and_pay(body)

@router.post("/{order_id}/pay", response_model=OrderResponseDTO)
async def pay_issued_order(order_id: int):
    
    Pay an issued reorder warning
    Transitions order from ISSUED -> PAYED.
    
    return await controller.pay_issued(order_id)

@router.post("/{order_id}/arrival", response_model=OrderResponseDTO)
async def record_order_arrival(order_id: int):
    
    Record order arrival
    Transitions order from PAYED -> COMPLETED and increases product quantity.
    
    return await controller.record_arrival(order_id)
"""

