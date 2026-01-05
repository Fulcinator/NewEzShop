from pydantic import BaseModel
from typing import Optional


class ReturnProductAssociationDTO(BaseModel):
    id: Optional[int] = None
    return_id: int
    product_barcode: str
    quantity: int
    price_per_unit: float

    class Config:
        from_attributes = True