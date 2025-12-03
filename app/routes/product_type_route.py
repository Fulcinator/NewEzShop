from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional

from app.controllers.product_type_controller import ProductTypeController
from app.models.DTO.product_type_dto import (
    ProductTypeCreateDTO,
    ProductTypeUpdateDTO,
    ProductTypeResponseDTO,
)
from app.middleware.auth_middleware import authenticate_user
from app.models.user_type import UserType
from app.config.config import ROUTES

router = APIRouter(
    prefix=ROUTES["V1_PRODUCT_TYPES"],
    tags=["Product Types"]
)

controller = ProductTypeController()

ALLOW = [UserType.Administrator, UserType.ShopManager]

# FR3.1 create
@router.post(
    "/",
    response_model=ProductTypeResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user(ALLOW))]
)
async def create_product_type(dto: ProductTypeCreateDTO):
    return await controller.create(dto)

# FR3.1 update
@router.put(
    "/{product_type_id}",
    response_model=ProductTypeResponseDTO,
    dependencies=[Depends(authenticate_user(ALLOW))]
)
async def update_product_type(product_type_id: int, dto: ProductTypeUpdateDTO):
    return await controller.update(product_type_id, dto)

# FR3.2 delete
@router.delete(
    "/{product_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(authenticate_user(ALLOW))]
)
async def delete_product_type(product_type_id: int):
    await controller.delete(product_type_id)
    return {}

# FR3.3 list all
@router.get(
    "/",
    response_model=List[ProductTypeResponseDTO],
    dependencies=[Depends(authenticate_user(ALLOW))]
)
async def list_product_types():
    return await controller.list_all()

# FR3.4 search
@router.get(
    "/search",
    response_model=List[ProductTypeResponseDTO],
    dependencies=[Depends(authenticate_user(ALLOW))]
)
async def search_product_types(
    barcode: Optional[str] = Query(None),
    description: Optional[str] = Query(None)
):
    return await controller.search(barcode, description)

