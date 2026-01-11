from fastapi import APIRouter, Depends, status
from typing import Any
from app.config.config import ROUTES
from app.controllers.inventory_controller import InventoryController
from app.models.DTO.inventory_dto import QuantityUpdateDTO
from app.models.DTO.position_dto import PositionDTO
from app.models.DTO.product_type_dto import ProductTypeResponseDTO
from app.middleware.auth_middleware import authenticate_user
from app.models.user_type import UserType

router = APIRouter(
    prefix=ROUTES["V1_PRODUCT_TYPES"],
    tags=["Inventory"],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))]
)

controller = InventoryController()


@router.put(
    "/{product_type_id}/quantity",
    response_model=ProductTypeResponseDTO,
    status_code=status.HTTP_200_OK
)
async def modify_quantity(product_type_id: int, body: QuantityUpdateDTO) -> ProductTypeResponseDTO:
    """
    Modify quantity available for a product type
    """
    return await controller.update_quantity(product_type_id, body)


@router.put(
    "/{product_type_id}/position",
    response_model=ProductTypeResponseDTO,
    status_code=status.HTTP_200_OK
)
async def modify_position(product_type_id: int, body: PositionDTO) -> ProductTypeResponseDTO:
    """
    Modify position for a product type
    """
    return await controller.update_position(product_type_id, body)
