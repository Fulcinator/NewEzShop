from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from sqlalchemy.orm import Session
from app.models.DTO.returnTransaction_dto import ReturnTransactionDTO
from app.models.user_type import UserType
from app.controllers.return_controller import ReturnController
from app.middleware.auth_middleware import authenticate_user
from app.config.config import ROUTES
from app.database.database import get_db
from app.models.errors.bad_request import BadRequestError
from app.models.errors.notfound_error import NotFoundError


router = APIRouter(prefix=ROUTES['V1_RETURNS'], tags=["Returns"])


@router.post("/", 
    response_model=ReturnTransactionDTO, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def start_return(
    sale_id: int = Query(...),
    db: Session = Depends(get_db)
):
    controller = ReturnController(db)
    return_obj = controller.start_return(sale_id)
    if not return_obj:
        raise HTTPException(status_code=420, detail="Return allowed only on closed and paid sales")
    return return_obj


@router.get("/", 
    response_model=List[ReturnTransactionDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_all_returns(db: Session = Depends(get_db)):
    controller = ReturnController(db)
    return controller.get_all_returns()


@router.get("/{return_id}", 
    response_model=ReturnTransactionDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_return(return_id: int, db: Session = Depends(get_db)):
    controller = ReturnController(db)
    return_obj = controller.get_return(return_id)
    if not return_obj:
        raise NotFoundError("Return not found")
    return return_obj


@router.get("/sale/{sale_id}", 
    response_model=List[ReturnTransactionDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_returns_by_sale(sale_id: int, db: Session = Depends(get_db)):
    controller = ReturnController(db)
    return controller.get_returns_by_sale(sale_id)


@router.delete("/{return_id}", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def delete_return(return_id: int, db: Session = Depends(get_db)):
    controller = ReturnController(db)
    success = controller.delete_return(return_id)
    if not success:
        raise HTTPException(status_code=420, detail="Cannot delete a reimbursed return")
    return {"success": True}


@router.post("/{return_id}/items", 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def add_product_to_return(
    return_id: int,
    barcode: str = Query(...),
    amount: int = Query(...),
    db: Session = Depends(get_db)
):
    if amount <= 0:
        raise BadRequestError("Amount must be positive")
    
    controller = ReturnController(db)
    success = controller.add_product_to_return(return_id, barcode, amount)
    if not success:
        raise HTTPException(status_code=420, detail="Cannot modify a closed return")
    return {"success": True}


@router.delete("/{return_id}/items", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def remove_product_from_return(
    return_id: int,
    barcode: str = Query(...),
    amount: int = Query(...),
    db: Session = Depends(get_db)
):
    if amount <= 0:
        raise BadRequestError("Amount must be positive")
    
    controller = ReturnController(db)
    success = controller.remove_product_from_return(return_id, barcode, amount)
    if not success:
        raise HTTPException(status_code=420, detail="Cannot remove items from a closed return")
    return {"success": True}


@router.patch("/{return_id}/close", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def close_return(return_id: int, db: Session = Depends(get_db)):
    controller = ReturnController(db)
    success = controller.close_return(return_id)
    if not success:
        raise HTTPException(status_code=420, detail="Invalid Return state to be closed")
    return {"success": True}


@router.patch("/{return_id}/reimburse", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def reimburse_return(return_id: int, db: Session = Depends(get_db)):
    controller = ReturnController(db)
    result = controller.reimburse_return(return_id)
    if not result:
        raise HTTPException(status_code=420, detail="Return must be closed before reimbursement")
    return result
