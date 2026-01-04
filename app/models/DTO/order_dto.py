from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.order_status import OrderStatus

class OrderCreateDTO(BaseModel):
    # id is optional and ignored if provided
    id: Optional[int] = Field(default=None, ge=1)
    product_barcode: str = Field(min_length=1, max_length=14)
    quantity: int = Field(ge=1)
    price_per_unit: float = Field(gt=0)

class OrderResponseDTO(BaseModel):
    id: int
    product_barcode: str
    quantity: int
    price_per_unit: float
    status: OrderStatus
    issue_date: datetime

    model_config = ConfigDict(from_attributes=True)