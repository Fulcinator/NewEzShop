from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, TYPE_CHECKING
from app.models.DTO.loyalty_card_dto import LoyaltyCardUpdateDTO

if TYPE_CHECKING:
    from app.models.DTO.loyalty_card_dto import LoyaltyCardResponseDTO
    


class CustomerCreateDTO(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class CustomerUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    card: Optional[LoyaltyCardUpdateDTO] = None

class CustomerResponseDTO(BaseModel):
    id: int
    name: str
    card: Optional["LoyaltyCardResponseDTO"] = Field(
        default=None,
        alias="loyalty_card"
    )

    model_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True,
    ser_json_tuples=False,
    json_schema_extra=None
)

from app.models.DTO.loyalty_card_dto import LoyaltyCardResponseDTO
CustomerCreateDTO.model_rebuild()
CustomerUpdateDTO.model_rebuild()
CustomerResponseDTO.model_rebuild()