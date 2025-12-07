from fastapi import APIRouter, Depends, Query, status, Response
from app.middleware.auth_middleware import authenticate_user
from app.models.user_type import UserType
from app.controllers.accounting_controller import AccountingController
from app.models.DTO.accounting_dto import BalanceResponseDTO
from app.config.config import ROUTES

router = APIRouter(
    prefix=ROUTES["V1_GENERAL"],
    tags=["accounting"],
)

controller = AccountingController()
ADMIN = [UserType.Administrator]

@router.get("/balance", response_model=BalanceResponseDTO, status_code=status.HTTP_200_OK, dependencies=[Depends(authenticate_user(ADMIN))])
async def get_balance():
    balance = await controller.get_balance()
    return BalanceResponseDTO(balance=balance)

@router.post("/balance/reset", status_code=status.HTTP_205_RESET_CONTENT, dependencies=[Depends(authenticate_user(ADMIN))])
async def reset_balance():
    await controller.reset_balance()
    return Response(status_code=status.HTTP_205_RESET_CONTENT)

@router.post("/balance/set", status_code=status.HTTP_201_CREATED, dependencies=[Depends(authenticate_user(ADMIN))])
async def set_balance(amount: float = Query(..., description="Amount to set as new balance")):
    await controller.set_balance(amount)
    return Response(status_code=status.HTTP_201_CREATED)
