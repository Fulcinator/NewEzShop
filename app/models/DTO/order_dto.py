from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.order_status import OrderStatus

class OrderCreateDTO(BaseModel):
    # id is optional and ignored if provided
    id: Optional[int] = Field(default=None, ge=1)
    product_barcode: str = Field(min_length=1, max_length=14)
    quantity: int = Field(ge=1)
    price_per_unit: float = Field(gt=0)

class OrderProductTypeDTO(BaseModel):
    product_type_id: int
    barcode: str
    description: str
    quantity: int

class OrderResponseDTO(BaseModel):
    order_id: int
    supplier: str | None
    status: str
    quantity: int
    price_per_unit: float
    issue_date: str
    product_types: List[OrderProductTypeDTO]
