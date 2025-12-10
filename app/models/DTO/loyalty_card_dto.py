from pydantic import BaseModel, Field
from typing import Optional


class LoyaltyCardCreateDTO(BaseModel):
    card_code: str = Field(min_length=10, max_length=10)
    customer_id: Optional[int] = None
    points: Optional[int] = Field(default=0, ge=0)


class LoyaltyCardUpdateDTO(BaseModel):
    card_code: Optional[str] = Field(None, min_length=10, max_length=10)
    customer_id: Optional[int] = None
    points: Optional[int] = Field(None, ge=0)


class LoyaltyCardResponseDTO(BaseModel):
    id: int
    card_code: str
    points: int
    customer_id: Optional[int] = None

    class Config:
        from_attributes = True
