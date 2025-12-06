from pydantic import BaseModel, Field
from typing import Optional


class ProductTypeCreateDTO(BaseModel):
    barcode: str = Field(min_length=1, max_length=14)
    name: str = Field(min_length=1)
    description: Optional[str] = None
    sellPrice: float
    quantity: int
    discountRate: Optional[float] = None
    notes: Optional[str] = None


class ProductTypeUpdateDTO(BaseModel):
    barcode: Optional[str] = Field(None, min_length=1, max_length=14)
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    sellPrice: Optional[float] = None
    quantity: Optional[int] = None
    discountRate: Optional[float] = None
    notes: Optional[str] = None


class ProductTypeResponseDTO(BaseModel):
    id: int
    barcode: str
    name: str
    description: Optional[str]
    sellPrice: float
    quantity: int
    discountRate: Optional[float]
    notes: Optional[str]

    class Config:
        from_attributes = True
