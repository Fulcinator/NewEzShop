from pydantic import BaseModel, Field
from typing import Optional


class SaleProductAssociationDTO(BaseModel):
    id: Optional[int] = None
    sale_id: int = Field(alias="sale_transaction_id")
    product_barcode: str
    quantity: int
    unit_price: float
    discount_rate: float = 0.0

    class Config:
        from_attributes = True
