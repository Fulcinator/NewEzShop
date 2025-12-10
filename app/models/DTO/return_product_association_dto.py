from pydantic import BaseModel
from typing import Optional


class ReturnProductAssociationDTO(BaseModel):
    id: Optional[int] = None
    return_id: int
    product_type_id: int
    quantity: int

    class Config:
        from_attributes = True
