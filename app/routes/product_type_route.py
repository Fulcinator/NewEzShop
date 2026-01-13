from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional

from app.controllers.product_type_controller import ProductTypeController
from app.models.DTO.product_type_dto import (
    ProductTypeCreateDTO,
    ProductTypePositionPatchDTO,
    ProductTypeQuantityPatchDTO,
    ProductTypeUpdateDTO,
    ProductTypeResponseDTO,
    SuccessDTO,
)
from app.middleware.auth_middleware import authenticate_user
from app.models.user_type import UserType
from app.config.config import ROUTES

router = APIRouter(
    prefix=ROUTES["V1_PRODUCT_TYPES"],
    tags=["Product Types"]
)

controller = ProductTypeController()

ADMIN_AND_MANAGER = [UserType.Administrator, UserType.ShopManager]

# FR3.1 create
@router.post(
    "/",
    response_model=ProductTypeResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user(ADMIN_AND_MANAGER))]
)
async def create_product_type(dto: ProductTypeCreateDTO):
    return await controller.create(dto)

# FR3.4 search
@router.get(
    "/search",
    response_model=List[ProductTypeResponseDTO],
    dependencies=[Depends(authenticate_user(ADMIN_AND_MANAGER))]
)
async def search_product_types(
    query: Optional[str] = Query(None)
):
    return await controller.search(query)

@router.get(
    "/{product_type_id}",
    response_model=ProductTypeResponseDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))]
)
async def get_product_type(product_type_id: int):
    if product_type_id < 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid product ID")
    return await controller.get_by_id(product_type_id)

# FR3.1 update
@router.put(
    "/{product_type_id}",
    response_model=ProductTypeResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user(ADMIN_AND_MANAGER))]
)
async def update_product_type(product_type_id: int, dto: ProductTypeUpdateDTO):
    if product_type_id < 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid product ID")
    return await controller.update(product_type_id, dto)

# FR3.2 delete
@router.delete(
    "/{product_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(authenticate_user(ADMIN_AND_MANAGER))]
)
async def delete_product_type(product_type_id: int):
    if product_type_id < 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid product ID")
    await controller.delete(product_type_id)
    return {}

# FR3.3 list all
@router.get(
    "/",
    response_model=List[ProductTypeResponseDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))]
)
async def list_product_types():
    return await controller.list_all()

# get by barcode
@router.get(
    "/barcode/{barcode}",
    response_model=ProductTypeResponseDTO,
    dependencies=[Depends(authenticate_user(ADMIN_AND_MANAGER))]
)
async def get_product_type_by_barcode(barcode: str):
    from fastapi import HTTPException
    if len(barcode) < 12 or len(barcode) > 14 or not barcode.isdigit():
        raise HTTPException(status_code=400, detail="Invalid barcode format")
    return await controller.get_by_barcode(barcode)



@router.patch(
    "/{product_type_id}/position",
    response_model=SuccessDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user(ADMIN_AND_MANAGER))]
)
async def patch_product_type_position(product_type_id: int, position: Optional[str] = Query(None)):
    from fastapi import HTTPException
    from app.models.DTO.product_type_dto import ProductTypePositionPatchDTO
    if product_type_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    # Validate position format if provided
    if position and position.strip():
        parts = position.split('-')
        if len(parts) != 3:
            raise HTTPException(status_code=400, detail="Invalid position format")
        try:
            aisleID = int(parts[0])
            rackID = parts[1]
            levelID = int(parts[2])
            if aisleID <= 0 or levelID <= 0 or not rackID.isalpha():
                raise HTTPException(status_code=400, detail="Invalid position format")
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Invalid position format")
    dto = ProductTypePositionPatchDTO(position=position if position else None)
    return await controller.patch_position(product_type_id, dto)


@router.patch(
    "/{product_type_id}/quantity",
    response_model=SuccessDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user(ADMIN_AND_MANAGER))]
)
async def patch_product_type_quantity(product_type_id: int, quantity: int = Query(..., ge=0)):
    from fastapi import HTTPException
    from app.models.DTO.product_type_dto import ProductTypeQuantityPatchDTO
    if product_type_id < 0:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    dto = ProductTypeQuantityPatchDTO(quantity=quantity)
    return await controller.patch_quantity(product_type_id, dto)
