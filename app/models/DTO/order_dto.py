from pydantic import BaseModel, Field
from typing import Optional
from app.models.order_status import OrderStatus

class OrderCreateDTO(BaseModel):
    product_type_id: int = Field(ge=1)
    supplier: str = Field(min_length=1)
    quantity: int = Field(ge=1)
    price_per_unit: float = Field(gt=0)

class OrderResponseDTO(BaseModel):
    id: int
    product_type_id: int
    supplier: str
    status: OrderStatus
    quantity: int
    price_per_unit: float

class OrderListFilterDTO(BaseModel):
    status: Optional[OrderStatus] = None
