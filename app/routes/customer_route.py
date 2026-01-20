from fastapi import APIRouter, HTTPException, status, Depends, Response, Query
from typing import List, Optional
from app.models.DTO.customer_dto import (
    CustomerCreateDTO,
    CustomerUpdateDTO,
    CustomerResponseDTO
)
from app.models.DTO.loyalty_card_dto import (
    LoyaltyCardCreateDTO,
    LoyaltyCardResponseDTO
)
from app.models.user_type import UserType
from app.controllers.customer_controller import CustomerController
from app.controllers.loyalty_card_controller import LoyaltyCardController
from app.middleware.auth_middleware import authenticate_user
from app.config.config import ROUTES
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.general_error import GeneralError


router = APIRouter(prefix=ROUTES['V1_CUSTOMERS'], tags=["customers"])
customer_controller = CustomerController()
loyalty_card_controller = LoyaltyCardController()


@router.post(
    "",
    response_model=CustomerResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))]
)
async def create_customer(customer: CustomerCreateDTO):
    try:
        return await customer_controller.create_customer(customer)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "",
    response_model=List[CustomerResponseDTO],
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))]
)
async def list_customers():
    return await customer_controller.list_customers()


@router.get(
    "/{customer_id}",
    response_model=CustomerResponseDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))]
)
async def get_customer(customer_id: int):
    try:
        if customer_id < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer ID must be non-negative")
        return await customer_controller.get_customer_by_id(customer_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/{customer_id}",
    response_model=CustomerResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))]
)
async def update_customer(customer_id: int, customer: CustomerUpdateDTO):
    try:
        if customer_id < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer ID must be non-negative")
        return await customer_controller.update_customer(customer_id, customer)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))]
)
async def delete_customer(customer_id: int):
    try:
        await customer_controller.delete_customer(customer_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/cards",
    response_model=LoyaltyCardResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))]
)
async def create_customer_card(card: Optional[LoyaltyCardCreateDTO] = None):
    try:
        return await loyalty_card_controller.create_loyalty_card(card)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch(
    "/{customer_id}/attach-card/{card_id}",
    response_model=CustomerResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))]
)
async def attach_card_to_customer(customer_id: int, card_id: str):
    try:
        # Convert card_id to int since loyalty cards use int IDs internally
        #card_id_int = int(card_id) in dao is str, so we convert to str with zero padding
        card_id = str(card_id).zfill(10)
        return await customer_controller.attach_loyalty_card_to_customer(customer_id, card_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card ID must be a valid integer")
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch(
    "/cards/{card_id}",
    response_model=LoyaltyCardResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))]
)
async def modify_card_points(card_id: str, points: int = Query(...)):
    try:
        card_id = str(card_id).zfill(10)
        return await loyalty_card_controller.add_points(card_id, points)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card ID must be a valid integer")
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except GeneralError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
