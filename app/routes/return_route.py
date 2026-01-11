from fastapi import APIRouter, status, Depends, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.DTO.returnTransaction_dto import ReturnTransactionDTO
from app.models.user_type import UserType
from app.controllers.return_controller import ReturnController
from app.middleware.auth_middleware import authenticate_user
from app.config.config import ROUTES
from app.database.database import get_db

router = APIRouter(prefix=ROUTES['V1_RETURNS'], tags=["Returns"])


@router.post("/",
    response_model=ReturnTransactionDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def start_return(
    sale_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    controller = ReturnController(db)
    return await controller.start_return(sale_id)


@router.get("/",
    response_model=List[ReturnTransactionDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_all_returns(db: AsyncSession = Depends(get_db)):
    controller = ReturnController(db)
    return await controller.get_all_returns()


@router.get("/{return_id}",
    response_model=ReturnTransactionDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_return(return_id: int, db: AsyncSession = Depends(get_db)):
    controller = ReturnController(db)
    return await controller.get_return(return_id)


@router.get("/sale/{sale_id}",
    response_model=List[ReturnTransactionDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_returns_by_sale(sale_id: int, db: AsyncSession = Depends(get_db)):
    controller = ReturnController(db)
    return await controller.get_returns_by_sale(sale_id)


@router.delete("/{return_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def delete_return(return_id: int, db: AsyncSession = Depends(get_db)):
    controller = ReturnController(db)
    await controller.delete_return(return_id)
    return {"success": True}


@router.post("/{return_id}/items",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def add_product_to_return(
    return_id: int,
    barcode: str = Query(...),
    amount: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    controller = ReturnController(db)
    await controller.add_product_to_return(return_id, barcode, amount)
    return {"success": True}


@router.delete("/{return_id}/items",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def remove_product_from_return(
    return_id: int,
    barcode: str = Query(...),
    amount: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    controller = ReturnController(db)
    await controller.remove_product_from_return(return_id, barcode, amount)
    return {"success": True}


@router.patch("/{return_id}/close",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def close_return(
    return_id: int,
    db: AsyncSession = Depends(get_db)
):
    controller = ReturnController(db)
    await controller.close_return(return_id)
    return {"success": True}


@router.patch("/{return_id}/reimburse",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def reimburse_return(
    return_id: int,
    db: AsyncSession = Depends(get_db)
):
    controller = ReturnController(db)
    result = await controller.reimburse_return(return_id)
    return result