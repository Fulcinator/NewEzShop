from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
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
async def start_sale(db: Session = Depends(get_db)):
    controller = SaleController(db)
    return controller.start_sale()


@router.get("/", 
    response_model=List[SaleTransactionDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_all_sales(db: Session = Depends(get_db)):
    controller = SaleController(db)
    return controller.get_all_sales()


@router.get("/{sale_id}", 
    response_model=SaleTransactionDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_sale(sale_id: int, db: Session = Depends(get_db)):
    controller = SaleController(db)
    sale = controller.get_sale(sale_id)
    if not sale:
        raise NotFoundError("Sale not found")
    return sale


@router.delete("/{sale_id}", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    controller = SaleController(db)
    success = controller.delete_sale(sale_id)
    if not success:
        raise HTTPException(status_code=420, detail="Cannot delete a paid sale")
    return {"success": True}


@router.post("/{sale_id}/items", 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def add_product_to_sale(
    sale_id: int,
    barcode: str = Query(...),
    amount: int = Query(...),
    db: Session = Depends(get_db)
):
    if amount <= 0:
        raise BadRequestError("Amount must be positive")
    
    controller = SaleController(db)
    success = controller.add_product_to_sale(sale_id, barcode, amount)
    if not success:
        raise HTTPException(status_code=420, detail="Cannot modify a non-open sale")
    return {"success": True}


@router.delete("/{sale_id}/items", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def remove_product_from_sale(
    sale_id: int,
    barcode: str = Query(...),
    amount: int = Query(...),
    db: Session = Depends(get_db)
):
    if amount <= 0:
        raise BadRequestError("Amount must be positive")
    
    controller = SaleController(db)
    success = controller.remove_product_from_sale(sale_id, barcode, amount)
    if not success:
        raise HTTPException(status_code=420, detail="Cannot modify a closed sale")
    return {"success": True}


@router.patch("/{sale_id}/discount", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def apply_discount_to_sale(
    sale_id: int,
    discount_rate: float = Query(...),
    db: Session = Depends(get_db)
):
    if discount_rate < 0.0 or discount_rate > 1.0:
        raise BadRequestError("Discount rate must be between 0.0 and 1.0")
    
    controller = SaleController(db)
    success = controller.apply_discount_to_sale(sale_id, discount_rate)
    if not success:
        raise HTTPException(status_code=420, detail="Cannot modify a closed sale")
    return {"success": True}


@router.patch("/{sale_id}/items/{product_barcode}/discount", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def apply_product_discount(
    sale_id: int,
    product_barcode: str,
    discount_rate: float = Query(...),
    db: Session = Depends(get_db)
):
    if discount_rate < 0.0 or discount_rate > 1.0:
        raise BadRequestError("Discount rate must be between 0.0 and 1.0")
    
    controller = SaleController(db)
    success = controller.apply_discount_to_product(sale_id, product_barcode, discount_rate)
    if not success:
        raise HTTPException(status_code=420, detail="Cannot modify a closed sale")
    return {"success": True}


@router.patch("/{sale_id}/close", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def close_sale(sale_id: int, db: Session = Depends(get_db)):
    controller = SaleController(db)
    success = controller.close_sale(sale_id)
    if not success:
        raise HTTPException(status_code=420, detail="Cannot modify a closed sale")
    return {"success": True}


@router.patch("/{sale_id}/pay", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def pay_sale(
    sale_id: int,
    cash_amount: float = Query(...),
    db: Session = Depends(get_db)
):
    if cash_amount < 0:
        raise BadRequestError("Cash amount cannot be negative")
    
    controller = SaleController(db)
    result = controller.pay_sale(sale_id, cash_amount)
    if not result:
        raise HTTPException(status_code=420, detail="Sale must be closed before payment")
    return result


@router.get("/{sale_id}/points", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def compute_points(sale_id: int, db: Session = Depends(get_db)):
    controller = SaleController(db)
    result = controller.compute_points(sale_id)
    if not result:
        raise NotFoundError("Sale not found")
    return result
