from pydantic import BaseModel, Field
from typing import Optional


class ProductTypeCreateDTO(BaseModel):
    id: int = Field(ge=1)
    barcode: str = Field(min_length=1, max_length=14)
    description: str = Field(min_length=1)
    price_per_unit: float
    quantity: int
    discountRate: Optional[float] = None
    note: Optional[str] = None
    position: str


class ProductTypeUpdateDTO(BaseModel):
    barcode: Optional[str] = Field(None, min_length=1, max_length=14)
    description: Optional[str] = Field(None, min_length=1)
    price_per_unit: Optional[float] = None
    quantity: Optional[int] = None
    discountRate: Optional[float] = None
    note: Optional[str] = None
    position: Optional[str] = None #enable to unset position

class ProductTypePositionPatchDTO(BaseModel):
    position: Optional[str] = None
class ProductTypeQuantityPatchDTO(BaseModel):
    quantity: int
class ProductTypeResponseDTO(BaseModel):
    id: int
    barcode: str
    description: str
    price_per_unit: float
    quantity: int
    discountRate: Optional[float]
    note: Optional[str]
    position: Optional[str] = None

    class Config:
        from_attributes = True

class SuccessDTO(BaseModel):
    success: bool