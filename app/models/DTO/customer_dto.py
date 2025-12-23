from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.DTO.loyalty_card_dto import LoyaltyCardResponseDTO


class CustomerCreateDTO(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)


class CustomerUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    surname: Optional[str] = Field(None, min_length=1, max_length=100)
    card: Optional["LoyaltyCardResponseDTO"] = None


class CustomerResponseDTO(BaseModel):
    id: int
    name: str
    surname: str
    card: Optional["LoyaltyCardResponseDTO"] = None

    class Config:
        from_attributes = True

from app.models.DTO.loyalty_card_dto import LoyaltyCardResponseDTO

CustomerUpdateDTO.model_rebuild()
CustomerResponseDTO.model_rebuild()
