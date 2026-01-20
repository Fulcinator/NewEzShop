from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class LoyaltyCardCreateDTO(BaseModel):
    card_id: Optional[str] = Field(default=None, min_length=10, max_length=10)
    points: Optional[int] = Field(default=0, ge=0)

class LoyaltyCardUpdateDTO(BaseModel):
    card_id: Optional[str] = Field(None, min_length=10, max_length=10)
    points: Optional[int] = Field(None, ge=0)

class LoyaltyCardResponseDTO(BaseModel):
    card_id: str
    points: int

    model_config = ConfigDict(
        from_attributes=True
    )