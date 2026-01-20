from fastapi import APIRouter, status, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.DTO.saleTransaction_dto import SaleTransactionDTO
from app.models.user_type import UserType
from app.controllers.sale_controller import SaleController
from app.middleware.auth_middleware import authenticate_user
from app.config.config import ROUTES
from app.database.database import get_db
from app.models.errors.bad_request import BadRequestError
from app.models.errors.notfound_error import NotFoundError

router = APIRouter(prefix=ROUTES['V1_SALES'], tags=["Sales"])


@router.post("/", 
    response_model=SaleTransactionDTO, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def start_sale(db: AsyncSession = Depends(get_db)):
    controller = SaleController(db)
    return await controller.start_sale()


@router.get("/", 
    response_model=List[SaleTransactionDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_all_sales(db: AsyncSession = Depends(get_db)):
    controller = SaleController(db)
    return await controller.get_all_sales()


@router.get("/{sale_id}", 
    response_model=SaleTransactionDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_sale(sale_id: int, db: AsyncSession = Depends(get_db)):
    if sale_id < 0:
        raise HTTPException(status_code=400, detail="Invalid sale ID")
    controller = SaleController(db)
    sale = await controller.get_sale(sale_id)
    if not sale:
        raise NotFoundError("Sale not found")
    return sale


@router.delete("/{sale_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def delete_sale(sale_id: int, db: AsyncSession = Depends(get_db)):
    if sale_id < 0:
        raise HTTPException(status_code=400, detail="Invalid sale ID")
    controller = SaleController(db)
    await controller.delete_sale(sale_id)


@router.post("/{sale_id}/items",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def add_product_to_sale(
    sale_id: int,
    barcode: str = Query(...),
    amount: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    if sale_id < 0:
        raise HTTPException(status_code=400, detail="Invalid sale ID")
    controller = SaleController(db)
    await controller.add_product_to_sale(sale_id, barcode, amount)
    return {"success": True}


@router.delete("/{sale_id}/items",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def remove_product_from_sale(
    sale_id: int,
    barcode: str = Query(...),
    amount: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    if sale_id < 0:
        raise HTTPException(status_code=400, detail="Invalid sale ID")
    controller = SaleController(db)
    await controller.remove_product_from_sale(sale_id, barcode, amount)
    return {"success": True}



@router.patch("/{sale_id}/discount",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def apply_discount_to_sale(
    sale_id: int,
    discount_rate: float = Query(..., ge=0.0, lt=1.0),
    db: AsyncSession = Depends(get_db)
):
    if sale_id < 0:
        raise HTTPException(status_code=400, detail="Invalid sale ID")
    controller = SaleController(db)
    await controller.apply_discount_to_sale(sale_id, discount_rate)
    return {"success": True}


@router.patch("/{sale_id}/items/{barcode}/discount",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def apply_product_discount(
    sale_id: int,
    barcode: str,
    discount_rate: float = Query(..., ge=0.0, lt=1.0),
    db: AsyncSession = Depends(get_db)
):
    if sale_id < 0:
        raise HTTPException(status_code=400, detail="Invalid sale ID")
    controller = SaleController(db)
    await controller.apply_discount_to_product(sale_id, barcode, discount_rate)
    return {"success": True}


@router.patch("/{sale_id}/close",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def close_sale(
    sale_id: int,
    db: AsyncSession = Depends(get_db)
):
    if sale_id < 0:
        raise HTTPException(status_code=400, detail="Invalid sale ID")
    controller = SaleController(db)
    await controller.close_sale(sale_id)
    return {"success": True}


@router.patch("/{sale_id}/pay",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def pay_sale(
    sale_id: int,
    cash_amount: float = Query(...),
    db: AsyncSession = Depends(get_db)
):
    if sale_id < 0:
        raise HTTPException(status_code=400, detail="Invalid sale ID")
    controller = SaleController(db)
    result = await controller.pay_sale(sale_id, cash_amount)
    return result


@router.get("/{sale_id}/points",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def compute_points(
    sale_id: int,
    db: AsyncSession = Depends(get_db)
):
    if sale_id < 0:
        raise HTTPException(status_code=400, detail="Invalid sale ID")
    controller = SaleController(db)
    result = await controller.compute_points(sale_id)
    return result